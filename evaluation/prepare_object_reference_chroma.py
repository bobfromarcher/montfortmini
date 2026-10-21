"""Freeze one reference-chromaticity contrast; preparation never runs inference."""
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--usage', type=float, required=True)
    parser.add_argument('--remaining', type=float, required=True)
    parser.add_argument('--confirm-zero-cash-cap', action='store_true')
    args = parser.parse_args()
    if not args.confirm_zero_cash_cap or args.usage < 0 or args.remaining < 5:
        raise ValueError('Live included credits and zero cash cap required, with verification reserve')
    here = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(here))
    import object_reference_chroma_candidate as candidate
    from object_reference_chroma_inputs import reference_chroma_control
    baseline = here/'evaluation/object-reference-luma'
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(baseline/'inputs.zip') as old:
        def read(name, mode): return np.asarray(Image.open(io.BytesIO(old.read(name))).convert(mode), dtype=np.float32)/255
        source = np.stack([read(f'source/{i:04d}.png', 'RGB') for i in range(17)])
        mask = np.stack([read(f'masks/{i:04d}.png', 'L') for i in range(17)])
        fg = np.stack([read(f'foreground/{i:04d}.png', 'L') for i in range(17)])
        ref = read('reference.png', 'RGB')
        control, annotation = reference_chroma_control(source, mask, ref, fg, read('reference-foreground.png', 'L') > 0)
        tensor = io.BytesIO()
        np.savez_compressed(tensor, source=control, mask=mask, reference=ref)
        with zipfile.ZipFile(root/'inputs.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
            for name in old.namelist(): archive.writestr(name, tensor.getvalue() if name == 'conditioning.npz' else old.read(name))
    graph = json.loads((baseline/'workflow-api.json').read_text(encoding='utf-8'))
    graph['6']['class_type'] = 'OpenJutsuReferenceChromaInputs'
    (root/'control-workflow.json').write_text(json.dumps(graph, indent=2), encoding='utf-8')
    annotation.update(intervention='Reference chromaticity only versus retained reference-luma development case. No new annotations, prompt/model/seed/steps/size/motion or brightness changes.',
                      product_limit='Fixture-specific foreground color oracle inherited byte-exact. Not a generic object editor; no output pixels used.',
                      hypothesis='Gray reactive control underspecifies reference chromaticity. Injecting fixed median reference RGB/luma may reduce canonical neon green while preserving shade and motion.',
                      competing_explanations='The descriptive green prompt, weak reference attention, or denoiser capacity may dominate regardless of control chromaticity. This test does not distinguish those alternatives if it fails.',
                      prediction='Raw output less saturated and closer to reference RGB ratios, without regressions in frozen visual or preservation gates. Input luma equality is an isolation check, not evidence of output quality.')
    (root/'foreground-annotation.json').write_text(json.dumps(annotation, indent=2), encoding='utf-8')
    observed = dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), usage=args.usage, remaining=args.remaining, cash_cap=0,
                    source='Live Modal billing UI, rounded account observation; not isolated invoice attribution')
    (root/'billing-observation.json').write_text(json.dumps(observed, indent=2), encoding='utf-8')
    freeze = json.loads((baseline/'freeze.json').read_text(encoding='utf-8'))
    freeze.update(frozen_utc=observed['observed_utc'], scope='One reference-chromaticity-only development contrast against retained failed reference-luma video; known footage, not held-out.')
    freeze['budget'].update(baseline_usage=args.usage, baseline_remaining=args.remaining,
                           stopping_usage=args.usage+.75, stopping_remaining=args.remaining-.75, cycle_included_cap=2.25,
                           stopping_rule='One development GPU call <=660seconds/$0.75 included; no retry/seed search. Stop on technical or full visual quality failure. Only after all frozen gates pass may reserve up to$1.50 included for separately bounded verification; whole cycle <=$2.25, cash0, at least$2 remaining. No volume storage.')
    freeze['source_sha256'] = {n: hashlib.sha256((here/n).read_bytes()).hexdigest() for n in candidate.NAMES}
    artifacts = ('inputs.zip', 'control-workflow.json', 'foreground-annotation.json', 'billing-observation.json')
    freeze['artifact_sha256'] = {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in artifacts}
    (root/'freeze.json').write_text(json.dumps(freeze, indent=2), encoding='utf-8')
    with zipfile.ZipFile(root/'executed-source.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for n in candidate.NAMES: archive.write(here/n, n)
        archive.write(__file__, 'evaluation/prepare_object_reference_chroma.py')
    with zipfile.ZipFile(root/'inputs.zip') as current, zipfile.ZipFile(baseline/'inputs.zip') as old:
        changed = [n for n in old.namelist() if old.read(n) != current.read(n)]
        same_entries = set(current.namelist()) == set(old.namelist())
    previous = json.loads((baseline/'workflow-api.json').read_text(encoding='utf-8'))
    check = dict(changed_old_input_entries=changed, same_archive_entry_names=same_entries,
                 changed_graph_nodes=[n for n in graph if graph[n] != previous[n]],
                 outside_control_exact=bool(np.array_equal(control[mask == 0], source[mask == 0])),
                 luma_delta_vs_prior_max=annotation['luma_delta_vs_prior_max'], clipped_values=annotation['clipped_values'],
                 unchanged='All source/reference/edit/foreground PNGs, prompt, model, seed and sampling settings')
    assert changed == ['conditioning.npz'] and same_entries and check['changed_graph_nodes'] == ['6'] and check['outside_control_exact']
    (root/'paired-input-audit.json').write_text(json.dumps(check, indent=2), encoding='utf-8')
    print(json.dumps(check, indent=2))


if __name__ == '__main__': main()
