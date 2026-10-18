"""Offline evidence checks; no downloads, inference, or perceptual scoring.

python evaluation/audit_cascade.py --run /path/to/extracted/run --output audit.json
Optional --compare /path/to/control checks decoded conditioning and graph equality.
"""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def pixels(path):
    with Image.open(path) as image:
        return np.asarray(image.convert('RGB'))


def audit(root):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    candidate = json.loads((root / 'candidate.json').read_text(encoding='utf-8'))
    raw = sorted((root / 'raw').glob('*.png'))
    composite = sorted((root / 'composite').glob('*.png'))
    expected = manifest['frames']
    shape = (manifest['height'], manifest['width'], 3)
    matches = [a.name == b.name and np.array_equal(pixels(a), pixels(b))
               for a, b in zip(raw, composite)]
    sizes = all(pixels(path).shape == shape for path in raw + composite)
    movies = {}
    for filename in ('source.mp4', 'generated.mp4', 'composite.mp4'):
        data = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
            '-show_entries', 'stream=width,height,r_frame_rate,nb_read_frames',
            '-of', 'json', str(root / filename)], text=True))['streams'][0]
        rate_num, rate_den = map(int, data['r_frame_rate'].split('/'))
        data['gate'] = (int(data['nb_read_frames']) == expected and
                        data['width'] == manifest['width'] and
                        data['height'] == manifest['height'] and
                        rate_num / rate_den == manifest['fps'])
        movies[filename] = data
    resources = []
    resource_path = root / 'candidate-gpu.csv'
    if resource_path.exists():
        with resource_path.open(encoding='utf-8', newline='') as stream:
            resources = list(csv.DictReader(stream))
    vram = [float(row['memory_MiB']) for row in resources if row.get('memory_MiB')]
    stages = {}
    for name in ('klein', 'qwen'):
        stage = root / 'reference-preparation' / name
        if (stage / 'manifest.json').exists():
            stages[name] = json.loads((stage / 'manifest.json').read_text(encoding='utf-8'))
    artifacts = [p for p in root.rglob('*') if p.is_file() and
                 p.name in ('workflow-api.json', 'manifest.json', 'candidate.json',
                            'conditioning.npz', 'anchor.png', 'uploaded-reference',
                            'uploaded-video', 'source.mp4', 'generated.mp4', 'composite.mp4')]
    return {
        'candidate_status': candidate['status'],
        'technical_gate': candidate['status'] == 'succeeded' and len(raw) == len(composite) == expected and sizes and all(v['gate'] for v in movies.values()),
        'frames': {'expected': expected, 'raw': len(raw), 'composite': len(composite)},
        'declared_fps': manifest['fps'],
        'dimensions_match': sizes,
        'decoded_movies': movies,
        'raw_composite_all_pixels_identical': len(matches) == expected and all(matches),
        'worker_seconds': candidate['worker_elapsed_seconds'],
        'frozen_reference_reused': candidate.get('frozen_reference_reused', False),
        'latency_scope': 'video worker only; cached reference preparation excluded' if candidate.get('frozen_reference_reused') else 'full reference preparation and video worker',
        'sampled_peak_vram_MiB': max(vram) if vram else None,
        'gpu_samples': len(vram),
        'allocated_memory_MiB': candidate['allocated_memory_MiB'],
        'physical_RAM_peak_measured': any(row.get('cgroup_memory_peak_bytes') for row in resources),
        'runtime_source_sha256': candidate['source_sha256'],
        'video_manifest': manifest,
        'reference_stages': stages,
        'artifact_sha256': {p.relative_to(root).as_posix(): sha(p) for p in sorted(artifacts)},
        'perceptual_gate': 'NOT established by this command; use frozen rubric and blinded review',
        'preservation_limit': 'Identical full-mask raw/composite frames do not establish source background preservation.'
    }


def compare(a, b):
    pairs = {}
    for key in ('source', 'mask', 'reference'):
        with np.load(a / 'inputs/conditioning.npz') as aa, np.load(b / 'inputs/conditioning.npz') as bb:
            pairs[key + '_pixels_equal'] = aa[key].shape == bb[key].shape and np.array_equal(aa[key], bb[key])
    ga = json.loads((a / 'workflow-api.json').read_text(encoding='utf-8'))
    gb = json.loads((b / 'workflow-api.json').read_text(encoding='utf-8'))
    pairs['changed_graph_nodes'] = [k for k in sorted(set(ga) | set(gb)) if ga.get(k) != gb.get(k)]
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--compare', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run)
    if args.compare:
        result['paired_control'] = compare(args.compare, args.run)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('technical_gate', 'frames', 'worker_seconds', 'latency_scope', 'sampled_peak_vram_MiB')}, indent=2))
    if not result['technical_gate']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
