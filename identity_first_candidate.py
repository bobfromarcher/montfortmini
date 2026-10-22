"""Reuse frozen budget/SDK/video machinery for the identity-first experiment."""
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path
import modal
import pose_reference_candidate as previous

HERE = Path(__file__).parent
app = modal.App('montfortmini-identity-first')
image = (previous.image
         .add_local_file(HERE / 'pose_reference_candidate.py', '/root/pose_reference_candidate.py')
         .add_local_file(HERE / 'identity_first_alignment.py', '/root/identity_first_alignment.py'))


@app.function(image=image, cpu=1, memory=512, timeout=60, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    from identity_first_alignment import identity_first
    import qwen_reference_alignment as qwen
    from qwen_anchor_workflow import FILES
    with identity_first():
        graph = qwen.build_graph()
    return {'identity_is_first': graph['6']['inputs']['image1'] == ['5', 0],
            'latent_canvas_stays_guide': graph['12']['inputs']['pixels'] == ['4', 0],
            'models': all((Path('/opt/ComfyUI/models') / f[3]).is_file() for f in FILES)}


def record(data, start, kind):
    data = previous.record(data, start, kind)
    result = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED) as new:
        for entry in old.infolist():
            value = old.read(entry)
            if entry.filename == 'cycle.json':
                rec = json.loads(value)
                rec['source_sha256'].update({name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                            for name in ('identity_first_candidate.py', 'identity_first_alignment.py')})
                value = json.dumps(rec, indent=2).encode()
            new.writestr(entry.filename, value)
    return result.getvalue()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def reference(source, identity, guide):
    from identity_first_alignment import run_reference_alignment
    start = time.monotonic()
    return record(run_reference_alignment(source, identity, guide), start, 'identity-first reference')


def motion(payload, archive, guide):
    import cascade_reference_alignment as frozen
    from identity_first_alignment import run_reference_alignment
    start = time.monotonic()
    original = frozen.run_reference_alignment
    try:
        frozen.run_reference_alignment = lambda source, identity: run_reference_alignment(source, identity, guide)
        data = previous.baseline.render.local(payload, archive)
    finally:
        frozen.run_reference_alignment = original
    return record(data, start, 'cached-reference video' if archive else 'fresh full pipeline')


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def video(payload, archive):
    return motion(payload, archive, None)


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def complete(payload, guide):
    return motion(payload, None, guide)


@app.local_entrypoint()
def main(output: str, kind: str = 'reference', source: str = '', identity: str = '',
         guide: str = '', cases: str = '', case: str = '', frozen_reference: str = '',
         budget_directory: str = 'outputs/identity-first', confirm_credits_only: bool = False,
         usage_observed: float = -1, remaining_observed: float = -1):
    # Scoped delegation keeps the proven reservation/receipt/archive checks unchanged.
    names = ('preflight', 'reference', 'video', 'complete')
    saved = {name: getattr(previous, name) for name in names}
    try:
        for name in names:
            setattr(previous, name, globals()[name])
        previous.main(output=output, kind=kind, source=source, identity=identity, guide=guide,
                      cases=cases, case=case, frozen_reference=frozen_reference,
                      budget_directory=budget_directory, confirm_credits_only=confirm_credits_only,
                      usage_observed=usage_observed, remaining_observed=remaining_observed)
    finally:
        for name, value in saved.items():
            setattr(previous, name, value)
