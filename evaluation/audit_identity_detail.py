"""Offline paired audit for the registered Qwen identity-detail correction."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rgb(path):
    with Image.open(path) as image:
        return np.asarray(ImageOps.exif_transpose(image).convert('RGB'))


def native_sizes(width, height):
    # Independently transcribed geometry from pinned nodes_qwen.py, lines77–90.
    vl = math.sqrt(384 * 384 / (width * height))
    vae = math.sqrt(1024 * 1024 / (width * height))
    return {'vision': [round(width * vl), round(height * vl)],
            'vae': [round(width * vae / 8) * 8, round(height * vae / 8) * 8]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    a, b = args.control, args.candidate
    old, new = read_json(a / 'manifest.json'), read_json(b / 'manifest.json')
    old_image, new_image = rgb(a / 'identity-conditioning.png'), rgb(b / 'identity-conditioning.png')
    old_size, new_size = list(old_image.shape[1::-1]), list(new_image.shape[1::-1])
    with Image.open(b / 'identity-original.png') as image:
        direct = np.asarray(ImageOps.exif_transpose(image).convert('RGB').resize(tuple(new_size), Image.Resampling.LANCZOS))
    checks = {
        'source_original_bytes_equal': (a / 'source-original.png').read_bytes() == (b / 'source-original.png').read_bytes(),
        'source_conditioning_pixels_equal': np.array_equal(rgb(a / 'source-conditioning.png'), rgb(b / 'source-conditioning.png')),
        'identity_original_bytes_equal': (a / 'identity-original.png').read_bytes() == (b / 'identity-original.png').read_bytes(),
        'workflow_equal': read_json(a / 'workflow-api.json') == read_json(b / 'workflow-api.json'),
        'prompt_equal': old['prompt'] == new['prompt'],
        'seed_equal': old['seed'] == new['seed'],
        'models_equal': old['models'] == new['models'],
        'native_conditioning_geometry_equal': native_sizes(*old_size) == native_sizes(*new_size),
        'candidate_is_direct_original_resample': np.array_equal(direct, new_image)
    }
    result = {'technical_pair_pass': all(checks.values()), 'checks': checks,
              'control_identity_dimensions': old_size, 'candidate_identity_dimensions': new_size,
              'control_native_geometry': native_sizes(*old_size),
              'candidate_native_geometry': native_sizes(*new_size),
              'original_identity_sha256': hashlib.sha256((b / 'identity-original.png').read_bytes()).hexdigest(),
              'worker_seconds': read_json(b / 'cycle.json')['worker_elapsed_seconds'],
              'limits': 'Checks one registered input-policy ablation. No perceptual pass, causal generalization or independent review is inferred from input-detail retention.'}
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['technical_pair_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
