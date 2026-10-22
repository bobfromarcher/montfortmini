"""Audit retained recipe evidence. Reports invariants, not perceptual quality.

Usage: python evaluation/audit_native_recipe.py /path/to/private/native-recipe
Requires NumPy and Pillow; contacts no service and runs no inference.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile
import numpy as np
from PIL import Image


def tensors(path):
    with zipfile.ZipFile(path) as archive:
        with np.load(io.BytesIO(archive.read('conditioning.npz')), allow_pickle=False) as arrays:
            return {key: arrays[key].copy() for key in arrays.files}


def audit(root):
    frozen = json.loads((root/'candidate-freeze.json').read_text(encoding='utf-8'))
    left, right = (tensors(root/(kind+'-inputs.zip')) for kind in ('oracle', 'reference'))
    paired = {key: bool(np.array_equal(left[key], right[key])) for key in ('source', 'mask', 'pose', 'face')}
    result = {'scope': 'Artifact invariants only; does not certify video quality.',
              'paired_control_tensors_equal': paired,
              'oracle_reference_equals_first_source_frame': bool(np.array_equal(left['reference'], left['source'][0])),
              'reference_pixels_changed': not np.array_equal(left['reference'], right['reference']),
              'runs': {}}
    for kind in ('oracle', 'reference', 'verification'):
        folder = root/kind
        if not (folder/'candidate.json').is_file():
            continue
        runtime = json.loads((folder/'recipe-runtime.json').read_text(encoding='utf-8'))
        record = json.loads((folder/'candidate.json').read_text(encoding='utf-8'))
        graph = json.loads((folder/'workflow-api.json').read_text(encoding='utf-8'))
        with (folder/'candidate-gpu.csv').open(newline='', encoding='utf-8') as file:
            samples = list(csv.DictReader(file))
        peak = max((float(row['memory_MiB']) for row in samples), default=None)
        log_path = folder/'comfy.log'
        if not log_path.is_file():
            log_path = folder/'failure/comfy.log'
        log = log_path.read_text(encoding='utf-8') if log_path.is_file() else ''
        seconds = re.search(r'Prompt executed in ([\d.]+) seconds', log)
        item = {'technical_status': record['status'],
                'worker_seconds': record['worker_elapsed_seconds'],
                'comfy_graph_seconds': float(seconds.group(1)) if seconds else None,
                'gpu_samples': len(samples), 'peak_sampled_gpu_MiB': peak,
                'source_hashes_match_freeze': runtime['code_sha256'] == frozen['code_sha256'],
                'graph_matches_freeze': graph == frozen['graph'],
                'failure': record['failure'], 'output_retrieved': (folder/'manifest.json').is_file()}
        if item['output_retrieved']:
            manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
            equal_frames = []
            for number in range(manifest['frames']):
                with Image.open(folder/'raw'/f'{number:04d}.png') as a, Image.open(folder/'composite'/f'{number:04d}.png') as b:
                    equal_frames.append(bool(np.array_equal(np.asarray(a), np.asarray(b))))
            item.update(raw_composite_equal_frames=sum(equal_frames), frames=manifest['frames'],
                        sdk_job_id=manifest['sdk_job_id'])
        else:
            item.update(raw_composite_equal_frames=None, frames=None,
                        limitation='No scored video retained; failure is not a perceptual-quality result.')
        if kind == 'verification':
            expected = json.loads((root/'test-freeze.json').read_text(encoding='utf-8'))['input_archive_sha256']
            input_path = root/'verification-controls/inputs.zip'
        else:
            expected = frozen['inputs'][kind]
            input_path = root/(kind+'-inputs.zip')
        item['input_archive_matches_freeze'] = hashlib.sha256(input_path.read_bytes()).hexdigest() == expected
        item['worker_input_matches_freeze'] = record['input_archive_sha256'] == expected
        result['runs'][kind] = item
    result['invariants_pass'] = bool(result['runs']) and all(paired.values()) and result['oracle_reference_equals_first_source_frame'] and result['reference_pixels_changed'] and all(
        run['source_hashes_match_freeze'] and run['graph_matches_freeze'] and run['input_archive_matches_freeze'] and run['worker_input_matches_freeze']
        and run['output_retrieved'] and run['raw_composite_equal_frames'] == run['frames'] and run['technical_status'] == 'succeeded'
        for run in result['runs'].values())
    return result


if __name__ == '__main__':
    report = audit(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['invariants_pass'] else 1)
