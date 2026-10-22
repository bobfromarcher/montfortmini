"""Prepare one annotated reference-luma contrast, without inference.

The color annotator below is specific to the known development fixture;
the control algorithm itself takes explicit, color-independent foreground masks.
"""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import cv2
import numpy as np
from PIL import Image


def foreground(rgb,color,roi=None):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    lo,hi=(10,35) if color=='yellow' else (35,85)
    mask=((hsv[:,:,0]>=lo)&(hsv[:,:,0]<=hi)&(hsv[:,:,1]>=160)&(hsv[:,:,2]>=60)).astype('uint8')
    if roi is not None:mask*=roi.astype('uint8')
    n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    if n<2:raise ValueError('Missing fixture foreground')
    selected=(labels==1+np.argmax(stats[1:,cv2.CC_STAT_AREA])).astype('uint8')
    contours,_=cv2.findContours(selected,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    filled=np.zeros_like(selected);cv2.drawContours(filled,contours,-1,1,-1)
    if roi is not None:filled*=roi.astype('uint8')
    return filled


def png(array):
    stream=io.BytesIO();Image.fromarray(array).save(stream,format='PNG');return stream.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    args=parser.parse_args()
    if not args.confirm_zero_cash_cap or args.usage<0 or args.remaining<5:
        raise ValueError('Observe live billing, zero cash cap and verification reserve')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import object_reference_luma_candidate as candidate
    from object_reference_luma_inputs import reference_luma_control
    baseline=here/'evaluation/object-luminance-prompt'
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(baseline/'inputs.zip') as old:
        source=np.stack([np.asarray(Image.open(io.BytesIO(old.read(f'source/{i:04d}.png'))).convert('RGB')) for i in range(17)])
        masks=np.stack([np.asarray(Image.open(io.BytesIO(old.read(f'masks/{i:04d}.png'))).convert('L'))>0 for i in range(17)])
        reference=np.asarray(Image.open(io.BytesIO(old.read('reference.png'))).convert('RGB'))
        fg=np.stack([foreground(rgb,'yellow',mask) for rgb,mask in zip(source,masks)])
        ref_fg=foreground(reference,'green')
        control,annotation=reference_luma_control(source.astype(np.float32)/255,masks.astype(np.float32),reference.astype(np.float32)/255,fg,ref_fg)
        tensor=io.BytesIO();np.savez_compressed(tensor,source=control,mask=masks.astype(np.float32),reference=reference.astype(np.float32)/255)
        with zipfile.ZipFile(root/'inputs.zip','x',zipfile.ZIP_DEFLATED) as archive:
            for n in old.namelist():archive.writestr(n,tensor.getvalue() if n=='conditioning.npz' else old.read(n))
            for i,m in enumerate(fg):archive.writestr(f'foreground/{i:04d}.png',png(m*255))
            archive.writestr('reference-foreground.png',png(ref_fg*255))
    graph=json.loads((baseline/'workflow-api.json').read_text());graph['6']['class_type']='OpenJutsuReferenceLumaInputs'
    (root/'control-workflow.json').write_text(json.dumps(graph,indent=2))
    annotation.update(foreground_method='Known fixture oracle: largest high-saturation yellow source component within unchanged edit mask, external contour fill; largest green reference component. HSV10..35 or35..85,s>=160,v>=60. Source/ref only, no generated pixels.',
                      intervention='Foreground-only fixed brightness gain; original source/reference/edit masks/positive prompt/sampling fixed versus luma+description.',
                      foreground_areas=[int(m.sum()) for m in fg],reference_foreground_area=int(ref_fg.sum()),
                      product_limit='This annotation oracle is not generic segmentation and cannot be silently promoted to the app.')
    (root/'foreground-annotation.json').write_text(json.dumps(annotation,indent=2))
    observed={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'usage':args.usage,'remaining':args.remaining,'cash_cap':0,'source':'Modal live billing UI; rounded, not invoice attribution'}
    (root/'billing-observation.json').write_text(json.dumps(observed,indent=2))
    freeze=json.loads((baseline/'freeze.json').read_text())
    freeze.update(frozen_utc=observed['observed_utc'],scope='Foreground-only reference-luma gain versus frozen luma+description known development case; not held-out.')
    freeze['budget'].update(baseline_usage=args.usage,baseline_remaining=args.remaining,
                            stopping_usage=args.usage+.75,stopping_remaining=args.remaining-.75,cycle_included_cap=3.0,
                            stopping_rule='One development call maximum660seconds/$0.75 included. Stop further inference on quality or technical failure; no seed search. Only after a full frozen visual pass allow separately bounded verification/integration, cycle ceiling$3 included, cash0 and at least$2 reserve.')
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('inputs.zip','control-workflow.json','foreground-annotation.json','billing-observation.json')}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2))
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for n in candidate.NAMES:archive.write(here/n,n)
        archive.write(__file__,'evaluation/prepare_object_reference_luma.py')
    with zipfile.ZipFile(root/'inputs.zip') as archive,zipfile.ZipFile(baseline/'inputs.zip') as old:
        changed=[n for n in old.namelist() if archive.read(n)!=old.read(n)]
    previous=json.loads((baseline/'workflow-api.json').read_text())
    check={'changed_old_input_entries':changed,'added_annotation_entries':18,
           'changed_graph_nodes':[n for n in graph if graph[n]!=previous[n]],
           'source_reference_edit_masks_prompt_sampler_unchanged':True,
           'gain':annotation['gain'],'outside_control_exact':bool(np.array_equal(control[~masks],source.astype(np.float32)[~masks]/255))}
    assert changed==['conditioning.npz'] and check['changed_graph_nodes']==['6'] and check['outside_control_exact']
    (root/'paired-input-audit.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2))


if __name__=='__main__':main()
