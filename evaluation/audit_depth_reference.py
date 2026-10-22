"""Offline third-condition audit; do not infer visual or video success."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image
from audit_pose_reference import audit, read, pixels, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    a, b = args.control / 'qwen', args.candidate / 'qwen'
    original, actual = read(a / 'workflow-api.json'), read(b / 'workflow-api.json')
    normalized = copy.deepcopy(actual)
    extra = normalized.pop('18')
    third_inputs = [normalized[k]['inputs'].pop('image3') for k in ('6', '7')]
    starts_with_control = normalized['6']['inputs']['prompt'].startswith(original['6']['inputs']['prompt'])
    normalized['6']['inputs']['prompt'] = original['6']['inputs']['prompt']
    old, new = read(a / 'manifest.json'), read(b / 'manifest.json')
    provenance = read(args.candidate / 'depth-provenance.json')
    depth = pixels(b / 'depth-conditioning.png')
    with Image.open(args.candidate / 'depth-original.png') as image:
        expected_depth = np.asarray(image.convert('RGB').resize((depth.shape[1], depth.shape[0]), Image.Resampling.LANCZOS))
    checks = {
        'control_technical_pass': audit(args.control)['technical_pass'],
        'candidate_technical_pass': audit(args.candidate)['technical_pass'],
        'graph_other_than_third_input_and_description_equal': normalized == original,
        'prior_prompt_preserved_as_prefix': starts_with_control,
        'third_input_links': third_inputs == [['18', 0], ['18', 0]],
        'third_image_loader': extra == {'class_type': 'LoadImage', 'inputs': {'image': 'identity-body-depth.png'}},
        'models_and_seed_equal': old['models'] == new['models'] and old['seed'] == new['seed'],
        'original_source_equal': digest(args.control / 'original-source.png') == digest(args.candidate / 'original-source.png'),
        'depth_original_digest': digest(args.candidate / 'depth-original.png') == provenance['depth_sha256'],
        'depth_pixels_match_recorded_resize': np.array_equal(expected_depth, depth),
        'depth_canvas_matches_guide': depth.shape == pixels(b / 'source-conditioning.png').shape,
        'depth_model_sha': provenance['weight_sha256'] == '3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70',
    }
    for filename in ('source-conditioning.png', 'identity-conditioning.png'):
        checks[filename + '_unchanged'] = np.array_equal(pixels(a / filename), pixels(b / filename))
    result = {'technical_ablation_pass': all(checks.values()), 'checks': checks,
              'changed_graph_nodes': sorted(k for k in set(original) | set(actual) if original.get(k) != actual.get(k)),
              'limits': 'Exploratory protocol amendment. Added estimated depth and its textual role; not a depth-only causal effect. No video, identity, pose or anatomy pass is assigned.'}
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['technical_ablation_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
