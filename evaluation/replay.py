"""Print the exact analyzed matrix by default; inference requires two explicit flags."""
import argparse,csv,subprocess,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--output',required=True)
    p.add_argument('--run',action='store_true');p.add_argument('--confirm-credits-only',action='store_true');a=p.parse_args()
    root=Path(a.evidence).resolve();rows=list(csv.DictReader((root/'experiment-matrix.csv').open()))
    if len(rows)>24:raise ValueError('Matrix exceeds registered call budget')
    if a.run and not a.confirm_credits_only:raise ValueError('Verify included credit and $0 spend cap before --run')
    runner=Path(__file__).resolve().parents[1]/'evaluation_runner.py'
    for row in rows:
        command=[sys.executable,'-m','modal','run',str(runner),'--dataset',str(root/'data/dataset.json'),'--output',str(Path(a.output).resolve()),
                 '--case-ids',row['case'],'--profile',row['profile'],'--variant',row['variant'],'--seed',row['seed'],'--confirm-credits-only']
        print(subprocess.list2cmdline(command),flush=True)
        if a.run:subprocess.run(command,check=True)

if __name__=='__main__':main()
