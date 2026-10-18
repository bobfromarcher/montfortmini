"""Offline paired-role audit against retained pose-first inputs and executed graph."""
import argparse
import copy
import json
from pathlib import Path
import numpy as np
from audit_pose_reference import audit, read, pixels, digest


def swap_labels(text):
    # Independent literal normalization of the recorded prompt (no runtime helper import).
    for prefix in ('image ', 'Image '):
        text = text.replace(prefix + '1', prefix + 'X').replace(prefix + '2', prefix + '1').replace(prefix + 'X', prefix + '2')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    a, b = args.control / 'qwen', args.candidate / 'qwen'
    old, new = read(a / 'manifest.json'), read(b / 'manifest.json')
    original = read(a / 'workflow-api.json')
    expected = copy.deepcopy(original)
    for key in ('6', '7'):
        value = expected[key]['inputs']
        value['image1'], value['image2'] = value['image2'], value['image1']
    expected['6']['inputs']['prompt'] = swap_labels(expected['6']['inputs']['prompt'])
    actual = read(b / 'workflow-api.json')
    checks = {
        'control_technical_pass': audit(args.control)['technical_pass'],
        'candidate_technical_pass': audit(args.candidate)['technical_pass'],
        'graph_diff_exactly_role_assignment': expected == actual,
        'prompt_semantics_relabel_only': swap_labels(old['prompt']) == new['prompt'],
        'models_equal': old['models'] == new['models'],
        'seed_equal': old['seed'] == new['seed'],
        'original_source_equal': digest(args.control / 'original-source.png') == digest(args.candidate / 'original-source.png'),
    }
    for filename in ('source-original.png', 'identity-original.png'):
        checks[filename + '_bytes_equal'] = (a / filename).read_bytes() == (b / filename).read_bytes()
    for filename in ('source-conditioning.png', 'identity-conditioning.png'):
        checks[filename + '_pixels_equal'] = np.array_equal(pixels(a / filename), pixels(b / filename))
    result = {'technical_pair_pass': all(checks.values()), 'checks': checks,
              'changed_graph_nodes': [k for k in original if original[k] != actual.get(k)],
              'control': str(args.control), 'candidate': str(args.candidate),
              'limits': 'Reference slot order plus necessary image-number prompt relabeling. No slot-only causal estimate, visual pass, video result or independent review follows from this audit.'}
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['technical_pair_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
