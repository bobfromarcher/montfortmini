"""Freeze one prompt-only contrast on known development footage; no inference."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import zipfile


PROMPT=('A small smooth solid green sphere rests on the pale tabletop in the left foreground. '
        'The green sphere is the same compact size as the beige ball on the right. '
        'A bumblebee rolls the beige ball. Two purple balls sit behind them. '
        'Soft overhead indoor light, subtle contact shadows, fixed camera, realistic macro footage.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    args=parser.parse_args()
    if not args.confirm_zero_cash_cap or args.remaining<2.75:raise ValueError('Observe current billing and zero cash cap')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import object_prompt_candidate as candidate
    baseline=here/'evaluation/quality/samples/new-real-object__candidate__s42'
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(root/'inputs.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((baseline/'inputs').rglob('*')):
            if path.is_file() and path.name not in ('uploaded-reference','uploaded-video'):
                archive.write(path,path.relative_to(baseline/'inputs').as_posix())
    graph=json.loads((baseline/'workflow-api.json').read_text());original=graph['4']['inputs']['text']
    graph['4']['inputs']['text']=PROMPT
    (root/'control-workflow.json').write_text(json.dumps(graph,indent=2))
    intervention={'changed_path':'4.inputs.text','before':original,'after':PROMPT,
                  'rationale':'Reference-only registration lost target green. Before attributing this to model capacity, test the official VACE recommendation for descriptive output prompts instead of edit instructions. No claim that mentioning yellow caused the failure.',
                  'guide_url':'https://github.com/ali-vilab/VACE/blob/main/UserGuide.md#31-vace-recognizable-inputs',
                  'limits':'One tailored scene caption; cannot establish generic captioning or reference identity control. More descriptive content and removal of edit language change together.'}
    (root/'mask-annotation.json').write_text(json.dumps(intervention,indent=2))
    observation={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'usage':args.usage,'remaining':args.remaining,'cash_cap':0,
                 'source':'Modal live UI; rounded account totals, not isolated invoice'}
    (root/'billing-observation.json').write_text(json.dumps(observation,indent=2))
    freeze=json.loads((here/'evaluation/object-mask/freeze.json').read_text())
    freeze.update(frozen_utc=observation['observed_utc'],scope='Known development recording: positive-prompt-only comparison against original wide-mask reference baseline. Not held-out.')
    freeze['budget'].update(baseline_usage=args.usage,baseline_remaining=args.remaining,
                            stopping_usage=args.usage+.75,stopping_remaining=args.remaining-.75,
                            stopping_rule='One fresh prompt-only reproduction; at most660seconds/$0.75 included. Stop after this call or on failure, no reroll. Cash0 and verification reserve$2. Reproduction is never independent held-out evidence.')
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('inputs.zip','control-workflow.json','mask-annotation.json','billing-observation.json')}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2))
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for n in candidate.NAMES:archive.write(here/n,n)
        archive.write(__file__,'evaluation/prepare_object_prompt.py')
    old=json.loads((baseline/'workflow-api.json').read_text());changed=[n for n in graph if graph[n]!=old[n]]
    assert changed==['4'] and graph['4']['inputs']['clip']==old['4']['inputs']['clip']
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        assert all(archive.read(n)==(baseline/'inputs'/n).read_bytes() for n in archive.namelist())
    (root/'paired-input-audit.json').write_text(json.dumps({'changed_graph_nodes':changed,'changed_path':'4.inputs.text','all_input_entries_exact':True},indent=2))
    print('Frozen one prompt-only run; no GPU dispatched.')


if __name__=='__main__':main()
