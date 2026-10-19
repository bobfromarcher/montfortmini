"""Offline paired reference experiment audit. Acceptance also needs visual review.

python evaluation/audit_object_reference.py evaluation/object-reference
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import cv2
import numpy as np
from PIL import Image
from quality_analysis import component,error,images,video


def audit(root,contrast='reference'):
    read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    frozen=read(root/'freeze.json');record=read(root/'candidate.json')
    runtime=read(root/'object-runtime.json')
    baseline=Path(__file__).parent/'quality/samples/new-real-object__candidate__s42'
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        source=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'source/{i:04d}.png'))).convert('RGB')) for i in range(17)])
        masks=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'masks/{i:04d}.png'))).convert('L'))>0 for i in range(17)])
        changed=[n for n in archive.namelist() if archive.read(n)!=(baseline/'inputs'/n).read_bytes()]
        old=np.load(baseline/'inputs/conditioning.npz');new=np.load(io.BytesIO(archive.read('conditioning.npz')))
        tensor_same={k:bool(np.array_equal(old[k],new[k])) for k in old.files}
        reference=np.asarray(Image.open(io.BytesIO(archive.read('reference.png'))).convert('RGB'),dtype=np.float32)/255
        if new['reference'].ndim==4:reference=reference[None]
        ref_tensor_matches=bool(np.array_equal(reference,new['reference']))
    raw=images(root/'raw');comp=images(root/'composite');encoded,fps=video(root/'composite.mp4')
    dilated=np.stack([cv2.dilate(m.astype('uint8'),np.ones((17,17),np.uint8))>0 for m in masks])
    rows=[]
    for i in range(17):
        src=component(source[i],'yellow',masks[i]);green=component(raw[i],'green',dilated[i])
        finished=component(comp[i],'green',masks[i])
        rows.append({'frame':i,'source_yellow':src,'raw_green':green,'composite_green':finished,
                     'raw_yellow':component(raw[i],'yellow',dilated[i]),
                     'area_ratio':green['area']/src['area'] if src and green else None,
                     'centroid_error_diagonal':float(np.linalg.norm(np.asarray(green['center'])-src['center'])/np.hypot(480,272)) if src and green else None})
    expected_graph=read(baseline/'workflow-api.json')
    if contrast=='prompt':expected_graph['4']['inputs']['text']=read(root/'mask-annotation.json')['after']
    checks={'technical_success':record['status']=='succeeded',
            'paired_archive_changes_exact':set(changed)==({'reference.png','conditioning.npz'} if contrast=='reference' else set()),
            'conditioning_change_exact':tensor_same=={'source':True,'mask':True,'reference':contrast=='prompt'},
            'reference_tensor_matches_png':ref_tensor_matches,
            'paired_graph_changes_exact':read(root/'workflow-api.json')==expected_graph,
            'worker_input_matches_freeze':record['input_archive_sha256']==frozen['artifact_sha256']['inputs.zip'],
            'frozen_inputs_exact':all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen['artifact_sha256'].items()),
            'runtime_source_matches_freeze':runtime['source_sha256']==frozen['source_sha256'],
            'size_frames_fps':raw.shape==source.shape==comp.shape==encoded.shape==(17,272,480,3) and fps==8}
    with zipfile.ZipFile(root/'executed-source.zip') as archive:
        checks['source_snapshot_matches_freeze']=all(hashlib.sha256(archive.read(n)).hexdigest()==h for n,h in frozen['source_sha256'].items())
    green=sum(r['raw_green'] is not None for r in rows)
    ratios=[r['area_ratio'] for r in rows if r['area_ratio'] is not None]
    distances=[r['centroid_error_diagonal'] for r in rows if r['centroid_error_diagonal'] is not None]
    ratio=float(np.median(ratios)) if ratios else None
    distance=float(np.mean(distances)) if distances else None
    preservation=error(source,raw,~dilated);encoded_preservation=error(source,encoded,~dilated)
    composite_preservation=error(source,comp,~masks)
    gates={'reference_color':green>=15,'scale_proxy':ratio is not None and .8<=ratio<=1.25,
           'centroid':distance is not None and distance<=.1,
           'raw_preservation':preservation['mae_255']<=3 and preservation['p95_255']<=10,
           'encoded_preservation':encoded_preservation['mae_255']<=3 and encoded_preservation['p95_255']<=10,
           'composite_preservation':composite_preservation['max_255']==0}
    return {'contrast':contrast,'invariants_pass':all(checks.values()),'checks':checks,'diagnostic_gates':gates,
            'diagnostic_gates_pass':all(gates.values()),'raw_green_reference_frames':green,
            'composite_green_reference_frames':sum(r['composite_green'] is not None for r in rows),
            'median_area_ratio':ratio,'mean_centroid_error_diagonal':distance,
            'raw_preservation':preservation,'encoded_preservation':encoded_preservation,
            'composite_preservation':composite_preservation,'rows':rows,
            'limits':'Known development footage. Color/area heuristics cannot certify reference likeness, motion or plausible scene lighting. Agent visual scores and independent review remain separate.'}


if __name__=='__main__':
    result=audit(Path(sys.argv[1]),'prompt' if '--prompt-only' in sys.argv else 'reference');print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['invariants_pass'] and result['diagnostic_gates_pass'] else 1)
