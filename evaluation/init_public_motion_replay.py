"""Initialize one separately budgeted replay; never contacts Modal or a GPU."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--example', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--usage', type=float, required=True)
    parser.add_argument('--remaining', type=float, required=True)
    parser.add_argument('--confirm-zero-cash-cap', action='store_true')
    args = parser.parse_args()
    if not args.confirm_zero_cash_cap or args.usage < 0 or args.remaining < 3:
        raise ValueError('Check live billing, zero cash cap and at least $3 included remaining')
    src = args.example.resolve()
    root = args.output.resolve()
    here = Path(__file__).resolve().parents[1]
    frozen = json.loads((src/'freeze.json').read_text(encoding='utf-8'))
    for name, sha in frozen['source_sha256'].items():
        if hashlib.sha256((here/name).read_bytes()).hexdigest() != sha:
            raise ValueError('Checkout differs from recorded example: '+name)
    for name, sha in frozen['artifact_sha256'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest() != sha:
            raise ValueError('Example artifact changed: '+name)
    root.mkdir(parents=True, exist_ok=False)
    for name in frozen['artifact_sha256']:
        shutil.copyfile(src/name, root/name)
    frozen.update(frozen_utc=datetime.now(timezone.utc).isoformat(),
                  classification='Reproduction of known synthetic example; not new held-out footage')
    frozen['budget'].update(baseline_usage=args.usage, baseline_remaining=args.remaining,
                            stopping_usage=args.usage+1, stopping_remaining=args.remaining-1)
    (root/'freeze.json').write_text(json.dumps(frozen, indent=2), encoding='utf-8')
    print('Fresh replay packet initialized. No inference or deployment. Read TESTER-INSTRUCTIONS.md before running.')


if __name__ == '__main__':
    main()
