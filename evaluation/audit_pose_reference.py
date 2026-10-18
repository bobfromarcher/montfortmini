"""Offline provenance/paired-input audit; never assigns a visual-quality pass."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def pixels(path):
    with Image.open(path) as im:
        return np.asarray(ImageOps.exif_transpose(im).convert('RGB'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(run):
    root = read(run / 'manifest.json')
    stage = read(run / 'qwen/manifest.json')
    cycle = read(run / 'cycle.json')
    identity = pixels(run / 'qwen/identity-conditioning.png')
    with Image.open(run / 'qwen/identity-original.png') as im:
        expected = np.asarray(ImageOps.exif_transpose(im).convert('RGB').resize(
            (identity.shape[1], identity.shape[0]), Image.Resampling.LANCZOS))
    checks = {
        'completed': root['status'] == stage['status'] == cycle['status'] == 'succeeded',
        'original_source_digest': digest(run / 'original-source.png') == root['original_source_sha256'],
        'original_identity_digest': digest(run / 'qwen/identity-original.png') == root['original_identity_sha256'] == stage['identity_sha256'],
        'guide_digest': digest(run / 'qwen/source-original.png') == root['guide_sha256'] == stage['source_sha256'],
        'sdk_receipt_confirmed': stage['sdk_receipt']['status'] == 'succeeded' and bool(stage['sdk_receipt']['job_id']),
        'native_seed': stage['seed'] == 42,
        'direct_original_identity_pixels': np.array_equal(expected, identity),
        'anchor_stage_bytes_equal': (run / 'anchor.png').read_bytes() == (run / 'qwen/anchor.png').read_bytes(),
    }
    return {'technical_pass': all(checks.values()), 'checks': checks,
            'guide_dimensions': list(pixels(run / 'qwen/source-conditioning.png').shape[1::-1]),
            'identity_dimensions': list(identity.shape[1::-1]),
            'worker_seconds': cycle['worker_elapsed_seconds'],
            'limits': 'Provenance/recipe checks only. Estimated pose, likeness, motion, anatomy, realism and temporal quality need separate review. No video was audited here.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--compare', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run)
    if args.compare:
        a, b = args.run / 'qwen', args.compare / 'qwen'
        x, y = read(a / 'manifest.json'), read(b / 'manifest.json')
        checks = {key + '_equal': x[key] == y[key] for key in ('models', 'prompt', 'seed')}
        checks.update({
            'graph_equal': read(a / 'workflow-api.json') == read(b / 'workflow-api.json'),
            'original_source_equal': digest(args.run / 'original-source.png') == digest(args.compare / 'original-source.png'),
            'original_identity_equal': digest(a / 'identity-original.png') == digest(b / 'identity-original.png'),
            'identity_conditioning_equal': np.array_equal(pixels(a / 'identity-conditioning.png'), pixels(b / 'identity-conditioning.png')),
            'guide_canvas_geometry_equal': pixels(a / 'source-conditioning.png').shape == pixels(b / 'source-conditioning.png').shape,
            'guide_pixels_differ': not np.array_equal(pixels(a / 'source-conditioning.png'), pixels(b / 'source-conditioning.png')),
        })
        result['paired_checks'] = checks
        result['paired_technical_pass'] = all(checks.values()) and audit(args.compare)['technical_pass']
        result['technical_pass'] = result['technical_pass'] and result['paired_technical_pass']
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['technical_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
