"""Verify lower-body reference protection and actual masked graph; never scores quality."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels(path, mode='RGB'):
    with Image.open(path) as im: return np.asarray(im.convert(mode))


def audit(root):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    stage = json.loads((root / 'qwen/manifest.json').read_text(encoding='utf-8'))
    graph = json.loads((root / 'qwen/workflow-api.json').read_text(encoding='utf-8'))
    base, final = pixels(root / 'base.png'), pixels(root / 'anchor.png')
    mask = pixels(root / 'edit-mask.png', 'L')
    if base.shape != final.shape or mask.shape != base.shape[:2]:
        raise ValueError('Output/protection dimensions differ')
    outside = mask == 0; inside = mask > 0
    error = np.abs(base.astype('int16') - final.astype('int16'))
    receipt = stage.get('sdk_receipt') or {}
    checks = {
        'generation_status': manifest['status'] == stage['status'] == 'succeeded',
        'exact_protected_reference_pixels': bool(np.array_equal(base[outside], final[outside])),
        'binary_mask': set(np.unique(mask)).issubset({0, 255}),
        'lower_body_region_only': bool(not inside[:round(len(mask) * .55)].any()),
        'body_region_changed': bool(error[inside].max() > 0),
        'mask_input_is_explicit': graph['16'] == {'class_type': 'LoadImageMask', 'inputs': {'image': 'protected-fill-mask.png', 'channel': 'red'}},
        'latent_mask_is_connected': graph['17'] == {'class_type': 'SetLatentNoiseMask', 'inputs': {'samples': ['12', 0], 'mask': ['16', 0]}},
        'sampler_uses_masked_latent': graph['13']['inputs']['latent_image'] == ['17', 0],
        'seed_and_sampler_retained': all(graph['13']['inputs'][k] == v for k, v in {'seed': 42, 'steps': 40, 'cfg': 4., 'sampler_name': 'euler', 'scheduler': 'simple', 'denoise': 1.}.items()),
        'sdk_success_receipt': receipt.get('status') == 'succeeded' and bool(receipt.get('job_id')),
        'recorded_base_hash': digest(root / 'base.png') == manifest['base_sha256'],
        'recorded_mask_hash': digest(root / 'edit-mask.png') == manifest['mask_sha256']}
    return {'technical_gate': all(checks.values()), 'checks': checks,
            'outside_reference_max_error': int(error[outside].max()),
            'editable_fraction': float(inside.mean()),
            'source_sha256': stage['source_sha256'], 'identity_sha256': stage['identity_sha256'],
            'model_files': stage['models'], 'sdk_job_id': receipt.get('job_id'),
            'quality_gate': 'NOT established. Inspect raw Qwen, protected reference, and subsequent raw video separately.',
            'limits': 'Exact reference protection does not prove video identity, plausible completion, source motion or scene preservation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('technical_gate', 'outside_reference_max_error', 'editable_fraction', 'sdk_job_id')}, indent=2))
    if not result['technical_gate']: raise SystemExit(1)
