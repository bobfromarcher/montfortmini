"""Audit reference-only isolation, repeatability and directional response offline."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import cv2
import numpy as np
from PIL import Image


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def result(path):return path/'result' if (path/'result').is_dir() else path
def frames(path,stage='raw'):
    return np.stack([np.asarray(Image.open(result(path)/stage/f'{i:04d}.png').convert('RGB')) for i in range(17)])
def arrays(path):
    with np.load(path,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def regions(root):
    with zipfile.ZipFile(root/'repeat/inputs.zip') as z:
        masks=np.stack([np.asarray(Image.open(io.BytesIO(z.read(f'foreground/{i:04d}.png'))).convert('L'))>0 for i in range(17)])
    return np.stack([cv2.erode(m.astype(np.uint8),np.ones((5,5),np.uint8))>0 for m in masks])


def arm_checks(directory):
    out=result(directory);frozen=read(directory/'freeze.json')
    with zipfile.ZipFile(directory/'inputs.zip') as z:
        with np.load(io.BytesIO(z.read('conditioning.npz'))) as n:prepared={k:n[k].copy() for k in n.files}
    actual=arrays(out/'inputs/runtime-conditioning.npz');receipt=arrays(out/'inputs/wan-conditioning.npz')
    metadata=read(out/'inputs/wan-conditioning.json')
    checks=dict(technical_success=read(out/'candidate.json')['status']=='succeeded',
                frozen_artifacts_match=all(hashlib.sha256((directory/n).read_bytes()).hexdigest()==h for n,h in frozen['artifact_sha256'].items()),
                runtime_sources_match=read(out/'object-runtime.json')['source_sha256']==frozen['source_sha256'],
                executed_input_tensors_exact=all(np.array_equal(prepared[k],actual[k]) for k in prepared),
                conditioning_receipt_hashes_match=all(hashlib.sha256(v.tobytes()).hexdigest()==metadata['tensors'][k]['sha256'] for k,v in receipt.items()),
                packing=receipt['reference_prefix'].shape==(1,32,1,34,60) and receipt['control_tail'].shape==(1,32,5,34,60) and receipt['initial_latent'].shape==(1,16,6,34,60),
                seed_and_trim=metadata['sampler_seed']==42 and metadata['trim_latent']==1,
                frames_dimensions=frames(directory).shape==(17,272,480,3))
    return checks,actual,receipt


def repeatability(root,parent):
    checks,actual,_=arm_checks(root/'repeat')
    prior=arrays(result(parent)/'inputs/runtime-conditioning.npz')
    checks['parent_inputs_exact']=all(np.array_equal(actual[k],prior[k]) for k in actual)
    a=frames(root/'repeat');old=frames(parent);core=regions(root)
    error=np.abs(a.astype(np.float32)-old.astype(np.float32))
    global_error=float(error.mean());core_error=float(error[core].mean())
    return dict(**{'pass':all(checks.values()) and global_error<=.5 and core_error<=1},
                checks=checks,global_raw_mae_255=global_error,foreground_raw_mae_255=core_error,
                max_raw_error_255=float(error.max()),raw_pixels_exact=bool(np.array_equal(a,old)),
                thresholds=dict(global_mae_max_255=.5,foreground_mae_max_255=1),
                limits='One same-seed repeat of known development footage; not a distributional GPU repeatability estimate.')


def audit_pair(root,parent):
    repeat=repeatability(root,parent);ca,aa,ra=arm_checks(root/'repeat');cb,ab,rb=arm_checks(root/'counterfactual')
    equal={k:bool(np.array_equal(ra[k],rb[k])) for k in ra}
    checks=dict(repeatability_pass=repeat['pass'],both_arm_invariants=all(ca.values()) and all(cb.values()),
                graph_byte_exact=(root/'repeat/control-workflow.json').read_bytes()==(root/'counterfactual/control-workflow.json').read_bytes(),
                controls_and_masks_exact=all(np.array_equal(aa[k],ab[k]) for k in ('source','mask')),
                reference_tensor_changed=not np.array_equal(aa['reference'],ab['reference']),
                sampler_inputs_isolated=all(v==(k!='reference_prefix') for k,v in equal.items()))
    core=regions(root)
    with zipfile.ZipFile(root/'repeat/inputs.zip') as z:
        ref_mask=np.asarray(Image.open(io.BytesIO(z.read('reference-foreground.png'))).convert('L'))>0
    ref_mask=cv2.erode(ref_mask.astype(np.uint8),np.ones((5,5),np.uint8))>0
    chroma=lambda pixels:(lambda m:m/m.sum())(np.median(pixels,axis=0).astype(np.float64))
    ref_a=chroma(aa['reference'][ref_mask]);ref_b=chroma(ab['reference'][ref_mask])
    direction=ref_b-ref_a;direction/=np.linalg.norm(direction)
    stages={}
    for stage in ('raw','composite'):
        a,b=frames(root/'repeat',stage),frames(root/'counterfactual',stage)
        error=np.abs(b.astype(np.float32)-a.astype(np.float32))
        projections=[float((chroma(b[i][core[i]])-chroma(a[i][core[i]]))@direction) for i in range(17)]
        mae=float(error[core].mean());threshold=max(1.,3*repeat['foreground_raw_mae_255'])
        directional=mae>threshold and sum(v>0 for v in projections)>=15
        outside=aa['mask']==0
        outside_mae=float(error[outside].mean())
        classification='directional reference response' if directional else 'nonspecific foreground sensitivity' if mae>threshold else 'below declared foreground sensitivity threshold'
        if np.array_equal(a,b):classification='pixel-identical output despite changed reference conditioning'
        elif mae<=threshold and outside_mae>threshold:classification='scene sensitivity without detected foreground response'
        stages[stage]=dict(foreground_mean_absolute_rgb_change_255=mae,whole_frame_mean_absolute_rgb_change_255=float(error.mean()),
                           outside_edit_mean_absolute_rgb_change_255=outside_mae,
                           output_pixels_exact=bool(np.array_equal(a,b)),reference_direction_projection_by_frame=projections,
                           frames_positive_direction=sum(v>0 for v in projections),change_threshold_255=threshold,
                           detected_directional_response=directional,
                           classification=classification)
    return dict(isolation_pass=all(checks.values()),checks=checks,repeatability=repeat,
                sampler_receipt_tensors_equal=equal,
                sampler_receipt_tensor_max_deltas={k:float(np.abs(ra[k]-rb[k]).max()) for k in ra},
                reference_chromaticities=dict(original=ref_a.tolist(),counterfactual=ref_b.tolist()),stages=stages,
                limits='Diagnostic sensitivity is not a video-quality pass. One seed/recording; correlated frames. A null result cannot prove a disconnected reference branch. Noise values not separately captured; same seed/initial latent and packing verified.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--repeat-only',action='store_true')
    a=p.parse_args();record=repeatability(a.root,a.parent) if a.repeat_only else audit_pair(a.root,a.parent)
    filename='repeatability.json' if a.repeat_only else 'branch-audit.json'
    (a.root/filename).write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2))
    raise SystemExit(0 if record.get('pass',record.get('isolation_pass')) else 1)


if __name__=='__main__':main()
