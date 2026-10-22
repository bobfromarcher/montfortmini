"""Offline CFG-only isolation and existing numerical video gates."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from audit_reference_branch import arm_checks,frames,read
from quality_analysis import component,error,video


def audit(root,parent):
    checks,actual,receipt=arm_checks(root)
    prior_checks,prior,prior_receipt=arm_checks(parent)
    expected=read(parent/'workflow-api.json');expected['9']['inputs']['cfg']=1.0
    checks.update(parent_invariants=all(prior_checks.values()),
                  full_input_zip_byte_exact=(root/'inputs.zip').read_bytes()==(parent/'inputs.zip').read_bytes(),
                  only_sampler_cfg_changed=read(root/'workflow-api.json')==expected,
                  all_executed_input_tensors_exact=all(np.array_equal(actual[k],prior[k]) for k in actual),
                  all_sampler_boundary_tensors_exact=all(np.array_equal(receipt[k],prior_receipt[k]) for k in receipt))
    source=np.stack([np.asarray(Image.open(root/'inputs/source'/f'{i:04d}.png')) for i in range(17)])
    mask=actual['mask']>0
    safe=np.stack([cv2.dilate(m.astype(np.uint8),np.ones((17,17),np.uint8))==0 for m in mask])
    raw,comp=frames(root),frames(root,'composite');encoded,fps=video(root/'composite.mp4')
    checks['encoded_size_fps']=encoded.shape==source.shape and fps==8
    rows=[]
    for i in range(17):
        src=component(source[i],'yellow',mask[i]);green=component(raw[i],'green',~safe[i])
        rows.append(dict(frame=i,source_yellow=src,raw_green=green,
                         composite_green=component(comp[i],'green',mask[i]),
                         area_ratio=green['area']/src['area'] if src and green else None,
                         centroid_error_diagonal=float(np.linalg.norm(np.asarray(green['center'])-src['center'])/np.hypot(480,272)) if src and green else None))
    ratios=[r['area_ratio'] for r in rows if r['area_ratio'] is not None]
    distances=[r['centroid_error_diagonal'] for r in rows if r['centroid_error_diagonal'] is not None]
    ratio=float(np.median(ratios)) if ratios else None;distance=float(np.mean(distances)) if distances else None
    raw_error=error(raw,source,safe);encoded_error=error(encoded,source,safe);comp_error=error(comp,source,~mask)
    green=sum(r['raw_green'] is not None for r in rows)
    gates=dict(reference_color=green>=15,scale_proxy=ratio is not None and .8<=ratio<=1.25,
               centroid=distance is not None and distance<=.1,
               raw_preservation=raw_error['mae_255']<=3 and raw_error['p95_255']<=10,
               encoded_preservation=encoded_error['mae_255']<=3 and encoded_error['p95_255']<=10,
               composite_preservation=comp_error['max_255']==0)
    return dict(isolation_pass=all(checks.values()),checks=checks,diagnostic_gates=gates,
                numerical_gates_pass=all(gates.values()),green_raw_frames=green,
                green_composite_frames=sum(r['composite_green'] is not None for r in rows),
                median_area_ratio=ratio,mean_centroid_error_diagonal=distance,
                raw_preservation=raw_error,encoded_preservation=encoded_error,composite_preservation=comp_error,
                raw_composite_target_pixels_exact=bool(np.array_equal(raw[mask],comp[mask])),rows=rows,
                limits='One known development clip/seed. Numerical gates and exact conditioning do not certify visual fidelity. At CFG1 the default sampler may skip unconditional prediction although its conditioning was captured. Actual prediction count not independently traced.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--parent',type=Path,default=Path(__file__).parent/'reference-branch/repeat')
    a=p.parse_args();record=audit(a.root,a.parent);(a.root/'offline-audit.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
    raise SystemExit(0 if record['isolation_pass'] and record['numerical_gates_pass'] else 1)
