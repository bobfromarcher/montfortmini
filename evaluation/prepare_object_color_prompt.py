"""Freeze one two-color-word ablation with expanded, output-independent diagnostics."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--usage',type=float,required=True)
    parser.add_argument('--remaining',type=float,required=True)
    parser.add_argument('--confirm-zero-cash-cap',action='store_true')
    a=parser.parse_args()
    if not a.confirm_zero_cash_cap or a.usage<0 or a.remaining<5:
        raise ValueError('Live included credits, zero cash cap and reserve required')
    here=Path(__file__).resolve().parents[1];sys.path.insert(0,str(here))
    import object_color_prompt_candidate as candidate
    parent=here/'evaluation/object-reference-chroma'
    root=a.output.resolve();root.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(parent/'inputs.zip',root/'inputs.zip')
    graph=json.loads((parent/'workflow-api.json').read_text(encoding='utf-8'))
    before=graph['4']['inputs']['text']
    if before.count(' green')!=2:raise ValueError('Expected exactly two green descriptors')
    after=before.replace(' green','')
    graph['4']['inputs']['text']=after
    (root/'control-workflow.json').write_text(json.dumps(graph,indent=2),encoding='utf-8')
    annotation=dict(before=before,after=after,removed='Two occurrences of the word green only; smooth/solid/size/lighting/motion words remain.',
                    unchanged='Full input archive and all graph fields except node4.inputs.text, including negative prompt and control node')
    (root/'prompt-annotation.json').write_text(json.dumps(annotation,indent=2),encoding='utf-8')
    protocol=dict(hypothesis='Explicit green descriptors favor canonical saturated green over reference appearance. Removing only those descriptors may permit reference/control color to determine output.',
                  primary_pair='Latest retained object-reference-chroma run versus color-word-removed candidate; not a comparison selected after new output.',
                  rejected_design='Removing smooth/solid too would confound color wording with material/shape wording. First-frame/generated-green-only color summaries would miss temporal drift and select only desired-color pixels.',
                  added_data='Source-anchored 2px-eroded foreground and reference ROIs; all17 frames, raw and composite separately: RGB medians, encoded-luma quantiles, saturation, RGB/sum chromaticity distance and adjacent-frame median-color variation. Per-frame CSV plus paired differences. Record actual preflight client time. No extra GPU call, new model, output-selected ROI or post-output color correction.',
                  diagnostic_predictions='If color-word pressure is a removable contributor, chromaticity distance should decrease across most frames and material appearance improve without shape/motion/preservation regression. Color-only improvement remains partial if visual gate fails.',
                  decision_table={'full_visual_pass':'Freeze recipe before selecting independent licensed unseen footage; not a population/parity claim.',
                                  'color_improves_visual_fails':'Partial color response, insufficient material/reference quality; stop this protocol.',
                                  'color_presence_or_shape_regresses':'Color descriptors were useful for target disambiguation at these settings; do not infer that reference conditioning is wholly absent.',
                                  'no_material_improvement':'Removing two green words is insufficient here. Does not separate remaining smooth/solid semantics, reference attention or capacity.'},
                  limits='One matched seed/recording, correlated frames, GPU repeatability not calibrated. Diagnostics not new acceptance gates. Fixed source ROI may include background on shape/position drift. Existing visual criteria and presence/shape/motion/preservation gates take precedence. No prompt implies exact reference-object identity.',
                  stopping_rule='One attempt <=660seconds/$0.75 included, no retry. Close on technical or full-quality failure. Only a full pass permits separately bounded verification from a$1.50 included reserve; total<=2.25, cash0 and at least$2 remaining.')
    (root/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    observed=dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),usage=a.usage,remaining=a.remaining,cash_cap=0,source='Modal live billing UI; rounded account values, not isolated invoice')
    (root/'billing-observation.json').write_text(json.dumps(observed,indent=2),encoding='utf-8')
    freeze=json.loads((parent/'freeze.json').read_text(encoding='utf-8'))
    freeze.update(frozen_utc=observed['observed_utc'],scope='Two green words removed only; known development recording, new preregistered all-frame diagnostics; not held-out.')
    freeze['budget'].update(baseline_usage=a.usage,baseline_remaining=a.remaining,stopping_usage=a.usage+.75,stopping_remaining=a.remaining-.75,cycle_included_cap=2.25,stopping_rule=protocol['stopping_rule'])
    freeze['source_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    analysis_names=('evaluation/object_color_diagnostics.py','evaluation/prepare_object_color_prompt.py')
    freeze['analysis_sha256']={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in analysis_names}
    with zipfile.ZipFile(root/'executed-source.zip','x',zipfile.ZIP_DEFLATED) as z:
        for n in (*candidate.NAMES,*analysis_names):z.write(here/n,n)
    artifacts=('inputs.zip','control-workflow.json','prompt-annotation.json','PROTOCOL.json','billing-observation.json','executed-source.zip')
    freeze['artifact_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in artifacts}
    (root/'freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
    original=json.loads((parent/'workflow-api.json').read_text(encoding='utf-8'))
    expected=json.loads(json.dumps(original));expected['4']['inputs']['text']=after
    check=dict(full_input_zip_byte_exact=(root/'inputs.zip').read_bytes()==(parent/'inputs.zip').read_bytes(),
               changed_graph_nodes=[n for n in graph if graph[n]!=original[n]],only_two_color_words_removed=graph==expected and after==before.replace(' green','') and before.count(' green')==2)
    assert check['full_input_zip_byte_exact'] and check['changed_graph_nodes']==['4'] and check['only_two_color_words_removed']
    (root/'paired-input-audit.json').write_text(json.dumps(check,indent=2),encoding='utf-8');print(json.dumps(check,indent=2))


if __name__=='__main__':main()
