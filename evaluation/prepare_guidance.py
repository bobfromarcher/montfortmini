"""Freeze one CFG5-to1 contrast, retaining exact reference/control/text inputs."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--usage',type=float,required=True)
    p.add_argument('--remaining',type=float,required=True);p.add_argument('--confirm-zero-cash-cap',action='store_true')
    a=p.parse_args()
    if not a.confirm_zero_cash_cap or a.usage<0 or a.remaining<5:raise ValueError('Live credits/zero cash cap/reserve required')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import guidance_candidate as candidate
    parent=here/'evaluation/reference-branch/repeat';root=a.output.resolve();root.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(parent/'inputs.zip',root/'inputs.zip')
    graph=json.loads((parent/'workflow-api.json').read_text(encoding='utf-8'))
    if graph['9']['inputs']['cfg']!=5:raise ValueError('Unexpected baseline CFG')
    graph['9']['inputs']['cfg']=1.0
    (root/'control-workflow.json').write_text(json.dumps(graph,indent=2))
    protocol=dict(hypothesis='Reducing CFG extrapolation5 to1 may permit the shared image-conditioned prediction to retain more reference appearance relative to the positive-negative difference. Reference branch is active but weak in the measured baseline. This is not a direct reference-gain knob or image-only generation.',
                  intervention='Only graph9.inputs.cfg5->1. Full input ZIP, positive/negative text, reference, reactive control, masks, latent packing, seed42, model and20steps exact versus original-green repeat.',
                  mechanism_source='https://github.com/Comfy-Org/ComfyUI/blob/5cc4b870094c89090db54bd8d12649dcaf89f2ba/comfy/samplers.py#L592',
                  mechanism='Pinned default CFG computes unconditional prediction plus CFG times conditional-minus-unconditional prediction. At CFG1 the default sampler skips unconditional evaluation. Negative conditioning is still provided/captured; its evaluation is not assumed. Positive text remains active. No custom CFG hook in this graph.',
                  predictions='If guidance extrapolation drives the beige/text preference, raw reference fidelity should improve without loss of shape, motion, stability or raw background preservation. Lower CFG could instead weaken useful constraints or blur the result.',
                  acceptance='Existing frozen visual anchors all>=3/4, >=15/17 defining-reference frames, no collapse/duplication; area proxy0.8..1.25, centroid<=0.1diag, raw/encoded outsideMAE<=3,p95<=10, composite outside PNG max0. Raw and composite evaluated separately. Extra color statistics cannot override visual failure.',
                  conditional_verification='Only after full green-reference visual+numerical pass, freeze the candidate and permit one separately bounded magenta-reference contrast with control/text fixed to verify reference selectivity. Only after that full pass select genuinely unseen licensed footage for remaining reserve; no new unseen claim from old footage.',
                  limits='One development recording/seed, fixture-specific masks. Any color gain could reflect control rather than reference and requires the conditional reference contrast. Changing CFG changes guidance computation, not just an isolated image weight. No grid/seed search or model-capacity proof.',
                  budget='One development attempt<=660seconds/$0.75 included. Stop on technical/full-quality failure. At most$1.50 reserved for separately bounded verification only after full pass, cycle ceiling$2.25, cash0, at least$2 remaining. No retry or intermediate CFG sweep.')
    (root/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2))
    observed=dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),usage=a.usage,remaining=a.remaining,cash_cap=0,source='Live Modal billing UI; rounded account totals')
    (root/'billing-observation.json').write_text(json.dumps(observed,indent=2))
    freeze=json.loads((parent/'freeze.json').read_text(encoding='utf-8'));freeze.update(arm='development',frozen_utc=observed['observed_utc'],scope='CFG5-to1 only, original green reference and text/control fixed; known development footage')
    freeze['budget'].update(baseline_usage=a.usage,baseline_remaining=a.remaining,stopping_usage=a.usage+.75,stopping_remaining=a.remaining-.75,cycle_included_cap=2.25,stopping_rule=protocol['budget'])
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    freeze['analysis_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in ('evaluation/prepare_guidance.py','evaluation/object_color_diagnostics.py')}
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as z:
        for n in (*candidate.NAMES,*freeze['analysis_sha256']):z.write(here/n,n)
    names=('inputs.zip','control-workflow.json','PROTOCOL.json','billing-observation.json','executed-source.zip')
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2))
    old=json.loads((parent/'workflow-api.json').read_text(encoding='utf-8'));expected=json.loads(json.dumps(old));expected['9']['inputs']['cfg']=1.0
    check=dict(input_zip_byte_exact=(root/'inputs.zip').read_bytes()==(parent/'inputs.zip').read_bytes(),changed_graph_nodes=[n for n in graph if graph[n]!=old[n]],cfg_only=graph==expected)
    assert check['input_zip_byte_exact'] and check['changed_graph_nodes']==['9'] and check['cfg_only']
    (root/'paired-input-audit.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2))


if __name__=='__main__':main()
