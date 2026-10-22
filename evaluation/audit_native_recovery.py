"""Offline recovery audit. Artifact checks do not establish perceptual quality.

python evaluation/audit_native_recovery.py /path/to/private/native-recovery
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
    frozen = json.loads((root / 'freeze.json').read_text(encoding='utf-8'))
    folder = root / 'result'
    runtime = json.loads((folder / 'recipe-runtime.json').read_text(encoding='utf-8'))
    recovery = json.loads((folder / 'recovery-runtime.json').read_text(encoding='utf-8'))
    record = json.loads((folder / 'candidate.json').read_text(encoding='utf-8'))
    graph = json.loads((folder / 'workflow-api.json').read_text(encoding='utf-8'))
    hashes = dict(runtime['code_sha256'])
    hashes['native_recipe_recovery.py'] = recovery['controller_sha256']
    files = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
             for name, digest in frozen['artifact_sha256'].items()}
    checks = {'runtime_source_matches_freeze': hashes == frozen['source_sha256'],
              'graph_matches_freeze': graph == frozen['graph'],
              'retained_artifacts_match_freeze': all(files.values()),
              'worker_input_matches_freeze': record['input_archive_sha256'] == frozen['artifact_sha256']['inputs.zip'],
              'technical_success': record['status'] == 'succeeded',
              'one_attempt': len(json.loads((root / 'gpu-ledger.json').read_text(encoding='utf-8'))) == 1}
    equal = []
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for i in range(manifest['frames']):
        with Image.open(folder / 'raw' / f'{i:04d}.png') as raw, Image.open(folder / 'composite' / f'{i:04d}.png') as composite:
            equal.append(bool(np.array_equal(np.asarray(raw), np.asarray(composite))))
    checks['raw_composite_full_mask_equality'] = len(equal) == 33 and all(equal)
    with (folder / 'candidate-gpu.csv').open(encoding='utf-8', newline='') as file:
        samples = list(csv.DictReader(file))
    log = (folder / 'comfy.log').read_text(encoding='utf-8')
    graph_seconds = re.search(r'Prompt executed in ([\d.]+) seconds', log)
    return {'scope': 'Artifact invariants only; independent quality review remains necessary.',
            'invariants_pass': all(checks.values()), 'checks': checks,
            'artifact_checks': files, 'raw_composite_equal_frames': sum(equal),
            'worker_seconds': record['worker_elapsed_seconds'],
            'graph_seconds': float(graph_seconds.group(1)) if graph_seconds else None,
            'gpu_sample_count': len(samples),
            'peak_sampled_gpu_MiB': max((float(row['memory_MiB']) for row in samples), default=None),
            'sdk_job_id': manifest['sdk_job_id']}


if __name__ == '__main__':
    result = audit(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['invariants_pass'] else 1)
