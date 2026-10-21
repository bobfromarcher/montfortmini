"""Freeze two matched reference-branch arms; no inference during preparation."""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
import numpy as np
from PIL import Image


def counterfactual_reference(reference, foreground):
    reference=np.asarray(reference,dtype=np.float32);foreground=np.asarray(foreground,dtype=bool)
    c=np.asarray([.2126,.7152,.0722],np.float32)
    luma=(reference*c).sum(-1)
    target=np.asarray([.70,.35,.65],np.float32)
    ratios=target/(target@c)
    changed=luma[...,None]*ratios
    if not foreground.any() or np.any((changed[foreground]<0)|(changed[foreground]>1)):
        raise ValueError('Counterfactual would clip; revise before freezing')
    result=np.where(foreground[...,None],changed,reference)
    error=float(np.max(np.abs((result*c).sum(-1)-luma)))
    if error>2e-7:raise ValueError('Reference luma isolation failed')
    return result,dict(method='Fixed magenta RGB/luma ratios on original reference foreground, preserving encoded luma/shading and all outside pixels; no clipping.',
                       target_rgb=target.tolist(),ratios=ratios.tolist(),encoded_luma_max_delta=error,
                       limits='Encoded RGB luma is not calibrated reflectance. PNG preview quantized; float32 NPZ tensor is authoritative.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--usage',type=float,required=True)
    p.add_argument('--remaining',type=float,required=True);p.add_argument('--confirm-zero-cash-cap',action='store_true')
    a=p.parse_args()
    if not a.confirm_zero_cash_cap or a.usage<0 or a.remaining<5:raise ValueError('Live credits/zero cash cap/reserve required')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import reference_branch_candidate as candidate
    parent=here/'evaluation/object-color-prompt';root=a.output.resolve();root.mkdir(parents=True,exist_ok=False)
    graph=json.loads((parent/'workflow-api.json').read_text(encoding='utf-8'))
    graph['6']['class_type']='OpenJutsuFrozenBranchInputs'
    graph['13']={'class_type':'OpenJutsuConditioningReceipt','inputs':{'positive':['7',0],'negative':['7',1],'latent':['7',2],'trim_latent':['7',3],'seed':graph['9']['inputs']['seed']}}
    for key,slot in (('positive',0),('negative',1),('latent_image',2)):graph['9']['inputs'][key]=['13',slot]
    with zipfile.ZipFile(parent/'inputs.zip') as z:
        with np.load(io.BytesIO(z.read('conditioning.npz'))) as n:original={k:n[k].copy() for k in n.files}
        foreground=np.asarray(Image.open(io.BytesIO(z.read('reference-foreground.png'))).convert('L'))>0
        alternate,annotation=counterfactual_reference(original['reference'],foreground)
        protocol=dict(primary_question='Does changing only the reference branch change object appearance when text and reactive control stay fixed?',
                      arms='Fresh repeat with original green reference, then magenta counterfactual. Same graph/node/conditioning capture for both; exact source/mask/text/seed/model. Existing beige run calibrates the new frozen loader and receipt.',
                      coupling_removed='Previous loader derived control gain/chroma from reference. Frozen loader reads exact prepared control/mask and an independent reference tensor. Original reference.png remains the control-preparation provenance; branch-reference.png is only a quantized display preview.',
                      conditioning_evidence='Float32 receipts capture positive/negative text, VACE reference prefix, control tail, mask, initial latent, shapes and sampler seed. Reference must change while all other captured tensors match exactly. Actual sampler noise is not separately captured; same seed and latent setup are verified.',
                      repeat_gate='Against retained beige parent: mean raw RGB error <=1/255 in fixed eroded source foreground and <=0.5/255 globally. Stop before second call on failed repeat, invariants or technical failure.',
                      sensitivity_rule='Directional object-color response requires fixed-ROI raw output mean absolute difference >max(1/255,3*repeat error), plus positive RGB/sum chromaticity projection along the reference-change direction in >=15/17 frames. Larger output change without direction is nonspecific sensitivity. Below threshold means no detected sensitivity at these settings, not proof of a disconnected branch.',
                      gates='Existing video quality rubric unchanged; diagnostic sensitivity is not reference fidelity or a quality pass. Wrong beige baseline quality is expected and alone does not stop the planned pair.',
                      budget='Maximum2 GPU calls,660seconds/$0.75 included each; $1.50 diagnostic cap plus$0.75 unspent verification reserve, total$2.25/cash0/reserve>=2. No retry/seed sweep. Stop after pair; no production promotion.',
                      limits='One development recording/seed; green control intentionally conflicts with changed reference to isolate the branch. Correlated frames, no population significance. Reference hue changes only in original foreground; small original-color rim can remain from annotation. Not a test of arbitrary geometry, independent professional quality or Genjutsu implementation.')
        (root/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2))
        (root/'counterfactual.json').write_text(json.dumps(annotation,indent=2))
        observed=dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),usage=a.usage,remaining=a.remaining,cash_cap=0,source='Live Modal billing UI; rounded account totals')
        (root/'billing-observation.json').write_text(json.dumps(observed,indent=2))
        for arm,ref in (('repeat',original['reference']),('counterfactual',alternate)):
            d=root/arm;d.mkdir();arrays=dict(original,reference=ref)
            stream=io.BytesIO();np.savez_compressed(stream,**arrays)
            preview=io.BytesIO();Image.fromarray(np.rint(ref*255).astype(np.uint8)).save(preview,format='PNG')
            with zipfile.ZipFile(d/'inputs.zip','x',zipfile.ZIP_DEFLATED) as out:
                for name in z.namelist():out.writestr(name,stream.getvalue() if name=='conditioning.npz' else z.read(name))
                out.writestr('branch-reference.png',preview.getvalue())
            (d/'control-workflow.json').write_text(json.dumps(graph,indent=2))
            for name in ('PROTOCOL.json','counterfactual.json','billing-observation.json'):(d/name).write_bytes((root/name).read_bytes())
            freeze=json.loads((parent/'freeze.json').read_text(encoding='utf-8'));freeze.update(arm=arm,frozen_utc=observed['observed_utc'],scope='Reference branch only; known development recording; pair planned before either new output')
            freeze['budget'].update(included_cap=.75,max_gpu_calls=1,max_gpu_seconds=660,baseline_usage=a.usage,baseline_remaining=a.remaining,stopping_usage=a.usage+1.5,stopping_remaining=a.remaining-1.5,cycle_included_cap=2.25,stopping_rule=protocol['budget'])
            freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
            freeze['analysis_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in ('evaluation/prepare_reference_branch.py','evaluation/object_color_diagnostics.py')}
            with zipfile.ZipFile(d/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as out:
                for n in (*candidate.NAMES,*freeze['analysis_sha256']):out.write(here/n,n)
            names=('inputs.zip','control-workflow.json','PROTOCOL.json','counterfactual.json','billing-observation.json','executed-source.zip')
            freeze['artifact_sha256']={n:hashlib.sha256((d/n).read_bytes()).hexdigest() for n in names}
            (d/'freeze.json').write_text(json.dumps(freeze,indent=2))
    assert (root/'repeat/control-workflow.json').read_bytes()==(root/'counterfactual/control-workflow.json').read_bytes()
    with np.load(parent/'inputs/runtime-conditioning.npz') as actual:
        actual_matches={k:bool(np.array_equal(actual[k],original[k])) for k in original}
    with zipfile.ZipFile(root/'repeat/inputs.zip') as za,zipfile.ZipFile(root/'counterfactual/inputs.zip') as zb:
        with np.load(io.BytesIO(za.read('conditioning.npz'))) as aa,np.load(io.BytesIO(zb.read('conditioning.npz'))) as bb:
            paired_tensors={k:bool(np.array_equal(aa[k],bb[k])) for k in original}
        changes=[n for n in za.namelist() if za.read(n)!=zb.read(n)]
    check=dict(arms=2,parent_actual_tensors_match=actual_matches,paired_tensors_equal=paired_tensors,
               paired_archive_entry_changes=changes,reference_luma_max_delta=annotation['encoded_luma_max_delta'])
    assert all(actual_matches.values()) and paired_tensors=={'source':True,'mask':True,'reference':False}
    assert set(changes)=={'conditioning.npz','branch-reference.png'}
    (root/'paired-input-audit.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2))


if __name__=='__main__':main()
