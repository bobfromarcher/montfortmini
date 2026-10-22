"""Prepare one fresh, credits-only reproduction; never dispatch inference."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    args=parser.parse_args()
    if not args.confirm_zero_cash_cap or args.remaining<=2 or args.usage<0:
        raise ValueError('Observe live billing, $0 cash cap and more than$2 included credits first')
    source=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(source))
    import object_mask_candidate
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False)
    for name in ('inputs.zip','control-workflow.json','mask-annotation.json'):
        shutil.copyfile(args.evidence/name,root/name)
    observation={'usage':args.usage,'remaining':args.remaining,'cash_cap':0,
                 'source':'Operator-supplied live observations; not a provider invoice'}
    (root/'billing-observation.json').write_text(json.dumps(observation,indent=2))
    frozen=json.loads((args.evidence/'freeze.json').read_text(encoding='utf-8'))
    frozen.update(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='Reproduction of known rejected mask oracle; never independent held-out evidence.')
    frozen['budget'].update(baseline_usage=args.usage,baseline_remaining=args.remaining,
                            stopping_usage=args.usage+.75,stopping_remaining=args.remaining-.75)
    frozen['source_sha256']={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in object_mask_candidate.NAMES}
    frozen['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in
                               ('inputs.zip','control-workflow.json','mask-annotation.json','billing-observation.json')}
    (root/'freeze.json').write_text(json.dumps(frozen,indent=2))
    print('Prepared fresh one-attempt reproduction; no GPU or remote call. Known failed video is not a new held-out case.')


if __name__=='__main__':main()
