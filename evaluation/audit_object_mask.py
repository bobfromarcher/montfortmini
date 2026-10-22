"""Offline retained object-mask checks; known rejected case exits1 for color.

python evaluation/audit_object_mask.py evaluation/object-mask
Artifact invariants and perceptual acceptance are reported separately.
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
from quality_analysis import component,error,video


def audit(root):
    read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    frozen=read(root/'freeze.json');record=read(root/'candidate.json')
    runtime=read(root/'object-runtime.json')
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        source=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'source/{i:04d}.png'))).convert('RGB')) for i in range(17)])
        mask=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'masks/{i:04d}.png'))).convert('L'))>0 for i in range(17)])
    raw=np.stack([np.asarray(Image.open(root/'raw'/f'{i:04d}.png').convert('RGB')) for i in range(17)])
    composite=np.stack([np.asarray(Image.open(root/'composite'/f'{i:04d}.png').convert('RGB')) for i in range(17)])
    dilated=np.stack([cv2.dilate(m.astype('uint8'),np.ones((17,17),np.uint8))>0 for m in mask])
    green=sum(component(raw[i],'green',dilated[i]) is not None for i in range(17))
    yellow=sum(component(raw[i],'yellow',dilated[i]) is not None for i in range(17))
    encoded,fps=video(root/'composite.mp4')
    checks={'technical_success':record['status']=='succeeded',
            'graph_matches_control':read(root/'workflow-api.json')==read(root/'control-workflow.json'),
            'worker_input_matches_freeze':record['input_archive_sha256']==frozen['artifact_sha256']['inputs.zip'],
            'input_archive_matches_freeze':hashlib.sha256((root/'inputs.zip').read_bytes()).hexdigest()==frozen['artifact_sha256']['inputs.zip'],
            'runtime_source_matches_freeze':runtime['source_sha256']==frozen['source_sha256'],
            'size_frames_fps':raw.shape==source.shape==(17,272,480,3) and encoded.shape==source.shape and fps==8}
    with zipfile.ZipFile(root/'executed-source.zip') as archive:
        checks['executed_source_snapshot_hashes_match']=all(hashlib.sha256(archive.read(n)).hexdigest()==h for n,h in frozen['source_sha256'].items())
    return {'invariants_pass':all(checks.values()),'checks':checks,
            'green_reference_frames':green,'yellow_source_color_frames':yellow,
            'color_reference_gate_pass':green>=15,
            'raw_preservation':error(source,raw,~dilated),
            'encoded_preservation':error(source,encoded,~dilated),
            'composite_preservation':error(source,composite,~mask),
            'scope':'Fixture-specific color and artifact checks; cannot certify overall visual quality. Known rejected case should fail the green-reference gate.'}


if __name__=='__main__':
    result=audit(Path(sys.argv[1]));print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['invariants_pass'] and result['color_reference_gate_pass'] else 1)
