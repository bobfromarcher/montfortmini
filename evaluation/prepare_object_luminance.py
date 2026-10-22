"""Freeze one source-luma contrast; no inference or production graph change."""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
from PIL import Image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    parser.add_argument('--output-description',action='store_true',help='Final paired prompt contrast; keeps source-luma control identical')
    args=parser.parse_args()
    if not args.confirm_zero_cash_cap or args.usage<0 or args.remaining<2.75:
        raise ValueError('Observe live billing, zero cash cap and verification reserve')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    if args.output_description:import object_luminance_prompt_candidate as candidate
    else:import object_luminance_candidate as candidate
    from object_luminance_inputs import luminance_control
    baseline=here/'evaluation/quality/samples/new-real-object__candidate__s42'
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False)
    old=np.load(baseline/'inputs/conditioning.npz')
    source=np.stack([np.asarray(Image.open(baseline/'inputs/source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(17)])
    control=luminance_control(source,old['mask'])
    stream=io.BytesIO();np.savez_compressed(stream,source=control,mask=old['mask'],reference=old['reference'])
    with zipfile.ZipFile(root/'inputs.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((baseline/'inputs').rglob('*')):
            if path.is_file() and path.name not in ('uploaded-reference','uploaded-video'):
                name=path.relative_to(baseline/'inputs').as_posix()
                archive.writestr(name,stream.getvalue() if name=='conditioning.npz' else path.read_bytes())
    graph=json.loads((baseline/'workflow-api.json').read_text());graph['6']['class_type']='OpenJutsuLuminanceInputs'
    if args.output_description:
        from prepare_object_prompt import PROMPT
        graph['4']['inputs']['text']=PROMPT
    (root/'control-workflow.json').write_text(json.dumps(graph,indent=2))
    intervention={'changed_graph_path':'6.class_type',
                  'change':'Neutral0.5 fill replaced by source luma within the original binary masks. Original outside RGB, reference, prompt, sampler and masks stay fixed.',
                  'rationale':'Prior reference-only and prompt-only video corrections failed scale/shape. Neutral fill deletes source target geometry; test achromatic geometry/shading as reactive control before changing models.',
                  'limits':'A geometry-retaining control can preserve unwanted source shape and constrain arbitrary shape replacement. This case is a sphere-to-sphere development edit, not general replacement evidence. Luma on encoded RGB is not physical luminance.'}
    if args.output_description:
        intervention.update(changed_graph_path='4.inputs.text versus source-luma-only;4.inputs.text+6.class_type versus original',
                            after=graph['4']['inputs']['text'],
                            change='Combine previously executed source-luma control with previously executed descriptive prompt; same source/mask/reference/control tensors as luma-only.',
                            rationale='Luma-only actual video produced a smaller yellow target. Complete the two-by-two conditioning/prompt comparison to test whether appearance can improve while retaining geometry. One final fixed-seed run; no new model or reference.',
                            paired_against='object-luminance')
    (root/'mask-annotation.json').write_text(json.dumps(intervention,indent=2))
    observation={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'usage':args.usage,'remaining':args.remaining,'cash_cap':0,'source':'Modal live UI; rounded account observations, not invoice attribution'}
    (root/'billing-observation.json').write_text(json.dumps(observation,indent=2))
    freeze=json.loads((here/'evaluation/object-mask/freeze.json').read_text())
    freeze.update(frozen_utc=observation['observed_utc'],scope='Source-luma-only diagnostic versus original wide-mask baseline on known development footage. No held-out claim.')
    if args.output_description:freeze['scope']='Final fixed-seed luma/descriptive-prompt factorial cell on known development footage. Positive-prompt-only contrast versus luma-only; not unseen validation.'
    freeze['budget'].update(baseline_usage=args.usage,baseline_remaining=args.remaining,
                            stopping_usage=args.usage+.75,stopping_remaining=args.remaining-.75,
                            stopping_rule='One660second GPU call maximum/$0.75 included planning ceiling. Stop after this call or on failure; no reroll or second intervention under this protocol. Cash0, reserve$2 for independent verification only after a frozen passing candidate.')
    if args.output_description:
        freeze['budget']['cycle_included_cap']=1.50
        freeze['budget']['stopping_rule']='Final GPU call of this continuation. Maximum660seconds/$0.75 included for this run, two total calls/$1.50 across luma-only+combination. Stop regardless of outcome: no further inference, model changes or tuning in this continuation. Cash0 and at least$2 verification reserve.'
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('inputs.zip','control-workflow.json','mask-annotation.json','billing-observation.json')}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2))
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for n in candidate.NAMES:archive.write(here/n,n)
        archive.write(__file__,'evaluation/prepare_object_luminance.py')
        if args.output_description:archive.write(here/'evaluation/prepare_object_prompt.py','evaluation/prepare_object_prompt.py')
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        changed=[n for n in archive.namelist() if archive.read(n)!=(baseline/'inputs'/n).read_bytes()]
        prepared=np.load(io.BytesIO(archive.read('conditioning.npz')))
    oldgraph=json.loads((baseline/'workflow-api.json').read_text())
    checks={'changed_archive_entries':changed,'changed_graph_nodes':[n for n in graph if graph[n]!=oldgraph[n]],
            'mask_and_reference_tensors_exact':bool(np.array_equal(old['mask'],prepared['mask']) and np.array_equal(old['reference'],prepared['reference'])),
            'outside_control_exact':bool(np.array_equal(control[old['mask']==0],old['source'][old['mask']==0])),
            'inside_control_achromatic':bool(np.array_equal(control[...,0][old['mask']==1],control[...,1][old['mask']==1]) and np.array_equal(control[...,1][old['mask']==1],control[...,2][old['mask']==1]))}
    expected_nodes=['4','6'] if args.output_description else ['6']
    assert changed==['conditioning.npz'] and checks['changed_graph_nodes']==expected_nodes and checks['mask_and_reference_tensors_exact'] and checks['outside_control_exact'] and checks['inside_control_achromatic']
    (root/'paired-input-audit.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
