"""Prepare a single reference-only paired diagnostic; never dispatch inference.

Specific to the retained synthetic green sphere on a uniform light background.
It is an annotation oracle, not a general object-segmentation algorithm.
"""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import zipfile

import cv2
import numpy as np
from PIL import Image


def register(reference, source_annotation):
    rgb=np.asarray(reference.convert('RGB')).copy()
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    foreground=(hsv[:,:,0]>=35)&(hsv[:,:,0]<=85)&(hsv[:,:,1]>=80)
    y,x=np.where(foreground)
    if not len(x):raise ValueError('Expected green reference subject')
    # Include antialiasing around the foreground; this area is uniformly230 gray
    # outside the original sphere. Keep the original canvas and gray sidebars.
    box=(int(x.min())-2,int(y.min())-2,int(x.max())+3,int(y.max())+3)
    patch=reference.crop(box)
    diameter=round(2*np.sqrt(source_annotation['source_color_area']/np.pi))
    patch=patch.resize((diameter,diameter),Image.Resampling.LANCZOS)
    result=reference.copy()
    result.paste((230,230,230),box)
    cx,cy=source_annotation['source_center']
    position=(round(cx-diameter/2),round(cy-diameter/2))
    result.paste(patch,position)
    return result,{'original_crop_xyxy':box,'new_patch_size':[diameter,diameter],
                   'new_patch_position':position,'source_annotation':source_annotation,
                   'method':'Green sphere crop plus2px; isotropic resize to first-source high-saturation equivalent-area diameter and translate to its centroid. Uniform original background restored; sidebars unchanged. No source RGB copied.',
                   'limits':'Source high-saturation area excludes shadows and some material pixels. Placement and scale change together. Subject pixel resampling is part of the intervention. Synthetic reference cannot establish realistic likeness.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    args=parser.parse_args()
    if not args.confirm_zero_cash_cap or args.remaining<2.75:raise ValueError('Observe live credits and zero cash cap')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import object_reference_candidate as candidate
    baseline=here/'evaluation/quality/samples/new-real-object__candidate__s42'
    prior=here/'evaluation/object-mask'
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False)
    annotation=json.loads((prior/'mask-annotation.json').read_text())['rows'][0]
    reference,record=register(Image.open(baseline/'inputs/reference.png').convert('RGB'),annotation)
    stream=io.BytesIO();reference.save(stream,format='PNG');reference_bytes=stream.getvalue()
    old=np.load(baseline/'inputs/conditioning.npz')
    arrays={k:old[k] for k in old.files}
    arrays['reference']=np.asarray(reference,dtype=np.float32)/255
    # Preserve the original reference tensor shape, including optional batch dim.
    if old['reference'].ndim==4:arrays['reference']=arrays['reference'][None]
    if arrays['reference'].shape!=old['reference'].shape:raise ValueError('Reference tensor shape changed')
    npz=io.BytesIO();np.savez_compressed(npz,**arrays)
    with zipfile.ZipFile(root/'inputs.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((baseline/'inputs').rglob('*')):
            if path.is_file() and path.name not in ('uploaded-reference','uploaded-video'):
                name=path.relative_to(baseline/'inputs').as_posix()
                archive.writestr(name,reference_bytes if name=='reference.png' else npz.getvalue() if name=='conditioning.npz' else path.read_bytes())
    shutil.copyfile(baseline/'workflow-api.json',root/'control-workflow.json')
    (root/'reference.png').write_bytes(reference_bytes)
    (root/'mask-annotation.json').write_text(json.dumps(record,indent=2))
    observation={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'usage':args.usage,'remaining':args.remaining,'cash_cap':0,
                 'source':'Operator-read Modal live billing UI; rounded, not invoice attribution'}
    (root/'billing-observation.json').write_text(json.dumps(observation,indent=2))
    freeze=json.loads((prior/'freeze.json').read_text())
    freeze.update(frozen_utc=observation['observed_utc'],scope='Known development recording: reference placement and scale only versus original wide-mask baseline. No held-out claim.')
    freeze['budget'].update(baseline_usage=args.usage,baseline_remaining=args.remaining,
                            stopping_usage=args.usage+.75,stopping_remaining=args.remaining-.75,
                            stopping_rule='One call at most660seconds; stop on technical or quality failure, no reroll. At least$2 reserved for verification only after frozen passing candidate.')
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('inputs.zip','control-workflow.json','mask-annotation.json','billing-observation.json')}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2))
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for n in candidate.NAMES:archive.write(here/n,n)
        archive.write(__file__,'evaluation/prepare_object_reference.py')
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        changed=[n for n in archive.namelist() if archive.read(n)!=(baseline/'inputs'/n).read_bytes()]
    if set(changed)!={'reference.png','conditioning.npz'}:raise ValueError('Unintended paired input change')
    checks={'changed_archive_entries':changed,'all_source_masks_settings_identical':True,
            'graph_bytes_identical':(root/'control-workflow.json').read_bytes()==(baseline/'workflow-api.json').read_bytes(),
            'conditioning_equal':{k:bool(np.array_equal(old[k],arrays[k])) for k in old.files}}
    (root/'paired-input-audit.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
