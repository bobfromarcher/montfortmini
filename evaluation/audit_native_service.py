"""Offline audit of a retained service.verify_native result. No inference.

python evaluation/audit_native_service.py /path/to/private/native-integration
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image


def audit(root):
    read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
    frozen = read(root/'freeze.json')
    result = root/'result'
    runtime = read(result/'service-runtime.json')
    calls = read(result/'service-job.json')
    record = read(result/'candidate.json')
    response = read(result/'app-response.json')
    graph = read(result/'workflow-api.json')
    source = {**runtime['source_sha256'], 'service.py': calls['service_sha256']}
    checks = {'runtime_sources_match_freeze': source == frozen['source_sha256'],
              'graph_matches_frozen_candidate': graph == frozen['expected_graph'],
              'response_graph_matches_execution': response['workflow'] == graph,
              'app_and_retained_sdk_job_match': response['manifest']['sdk_job_id'] == read(result/'manifest.json')['sdk_job_id'],
              'technical_success': record['status'] == 'succeeded',
              'one_orchestrated_attempt': len(read(root/'gpu-ledger.json')) == 1}
    checks['original_request_matches_freeze'] = all(
        hashlib.sha256((root/name).read_bytes()).hexdigest() == digest
        for name, digest in frozen['artifact_sha256'].items())
    equal = []
    for i in range(33):
        with Image.open(result/'raw'/f'{i:04d}.png') as raw, Image.open(result/'composite'/f'{i:04d}.png') as composite:
            equal.append(raw.size == (480,560) and np.array_equal(np.asarray(raw), np.asarray(composite)))
    checks['all_raw_and_composite_frames_equal'] = all(equal)
    checks['app_video_bytes_match_retained_videos'] = all(
        (result/('app-'+name)).read_bytes() == (result/name).read_bytes()
        for name in ('source.mp4','generated.mp4','composite.mp4'))
    with (result/'candidate-gpu.csv').open(encoding='utf-8',newline='') as file:
        samples = list(csv.DictReader(file))
    seconds = re.search(r'Prompt executed in ([\d.]+) seconds', (result/'comfy.log').read_text(encoding='utf-8'))
    control_path = result/'inputs/controls.json'
    return {'scope':'Artifact and exact app-path verification; not independent perceptual proof.',
            'invariants_pass':all(checks.values()),'checks':checks,
            'raw_composite_equal_frames':sum(bool(v) for v in equal),
            'worker_seconds':record['worker_elapsed_seconds'],
            'graph_seconds':float(seconds.group(1)) if seconds else None,
            'cpu_controls_seconds':read(control_path)['elapsed_cpu_seconds'] if control_path.exists() else None,
            'gpu_sample_count':len(samples),
            'peak_sampled_gpu_MiB':max((float(row['memory_MiB']) for row in samples),default=None),
            'calls':calls,'sdk_job_id':response['manifest']['sdk_job_id']}


if __name__ == '__main__':
    result = audit(Path(sys.argv[1]))
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['invariants_pass'] else 1)
