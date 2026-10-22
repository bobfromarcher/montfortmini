"""Offline artifact verification only; exit0 does not certify video quality."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image


def audit(root):
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    frozen = read(root/'freeze.json')
    result = root/'result'
    runtime = read(result/'service-runtime.json')
    worker = read(result/'candidate.json')
    inputs_sha = hashlib.sha256((root/'inputs.zip').read_bytes()).hexdigest()
    checks = {
        'runtime_sources_match_freeze': all(frozen['source_sha256'].get(k) == v for k, v in runtime['source_sha256'].items()),
        'initial_artifacts_exact': all(hashlib.sha256((root/k).read_bytes()).hexdigest() == v for k, v in frozen['artifact_sha256'].items()),
        'graph_matches_freeze': read(result/'workflow-api.json') == frozen['expected_graph'] == read(root/'workflow-api.json'),
        'worker_inputs_match_review': worker['input_archive_sha256'] == runtime['input_archive_sha256'] == inputs_sha == read(root/'controls-review.json')['inputs_sha256'],
        'technical_success': worker['status'] == 'succeeded',
        'one_cpu_and_gpu': all(read(root/(s+'-ledger.json'))['status'] == 'succeeded' for s in ('controls', 'render')),
    }
    equal = []
    for i in range(33):
        with Image.open(result/'raw'/f'{i:04d}.png') as raw, Image.open(result/'composite'/f'{i:04d}.png') as comp:
            equal.append(raw.size == comp.size == (480,480) and np.array_equal(raw,comp))
    checks['raw_composite_equal_all33'] = all(equal)
    return {'artifact_invariants_pass':all(checks.values()),'checks':checks,
            'quality_gate_pass':read(root/'review.json')['quality_gate_pass'],
            'scope':'Recorded artifact invariants; independent person/account reproduction and exact facial-quality proof remain outstanding.'}


if __name__ == '__main__':
    record = audit(Path(sys.argv[1]))
    print(json.dumps(record,indent=2))
    raise SystemExit(0 if record['artifact_invariants_pass'] else 1)
