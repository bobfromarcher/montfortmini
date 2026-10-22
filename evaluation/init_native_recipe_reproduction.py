"""Create an absent, fresh reproduction directory; performs no remote calls.

Uses a private evidence packet. Previously evaluated recordings are reproduction
cases here, not new held-out evidence. Review both outputs before each next call.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_recipe_candidate import NAMES
from native_recipe_fixture import validate_fixture
from native_recipe_workflow import build_graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--usage-observed', type=float, required=True)
    parser.add_argument('--remaining-observed', type=float, required=True)
    args = parser.parse_args()
    if args.remaining_observed <= 2 or args.usage_observed < 0:
        raise ValueError('Need more than $2 in included credits and a current usage observation')
    args.output.mkdir(parents=True, exist_ok=False)
    for name in ('oracle-inputs.zip', 'reference-inputs.zip', 'PROTOCOL.md', 'test-events-freeze.json'):
        shutil.copyfile(args.evidence/name, args.output/name)
    target = args.output/'verification-controls'
    target.mkdir()
    shutil.copyfile(args.evidence/'verification-inputs-fixed.zip', target/'inputs.zip')
    for path in (args.output/'oracle-inputs.zip', args.output/'reference-inputs.zip', target/'inputs.zip'):
        validate_fixture(path.read_bytes(), frames=33, width=480, height=560)
    source = Path(__file__).resolve().parents[1]
    frozen = {'code_sha256': {name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in NAMES},
              'graph': build_graph(), 'inputs': {kind: hashlib.sha256((args.output/(kind+'-inputs.zip')).read_bytes()).hexdigest() for kind in ('oracle', 'reference')},
              'classification': 'Independent reproduction of known recordings, not new held-out evaluation.'}
    (args.output/'candidate-freeze.json').write_text(json.dumps(frozen, indent=2))
    (args.output/'test-freeze.json').write_text(json.dumps({'input_archive_sha256': hashlib.sha256((target/'inputs.zip').read_bytes()).hexdigest(), 'classification': frozen['classification']}, indent=2))
    (args.output/'budget.json').write_text(json.dumps({'cash_cap': 0, 'included_cap': 2, 'stopping_usage': args.usage_observed+2,
        'stopping_remaining': args.remaining_observed-2, 'max_gpu_attempts': 3, 'max_worker_seconds': 2700}, indent=2))
    print('Reproduction directory prepared. No inference started. Verify the account cash cap before any paid-resource command.')


if __name__ == '__main__':
    main()
