"""One bounded depth-guidance ablation, reusing the established SDK and budget."""
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path
import modal
import identity_first_candidate as first

HERE = Path(__file__).parent
app = modal.App('montfortmini-identity-depth')
image = (first.image
         .add_local_file(HERE / 'depth_preprocessing.py', '/root/depth_preprocessing.py')
         .add_local_file(HERE / 'identity_first_candidate.py', '/root/identity_first_candidate.py')
         .add_local_file(HERE / 'depth_identity_alignment.py', '/root/depth_identity_alignment.py'))


@app.function(image=image, cpu=1, memory=512, timeout=60, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    from depth_identity_alignment import depth_policy
    from identity_first_alignment import identity_first
    import qwen_reference_alignment as qwen
    with depth_policy(), identity_first():
        graph = qwen.build_graph()
    return {'identity_is_first': graph['6']['inputs']['image1'] == ['5', 0],
            'depth_is_third': graph['6']['inputs']['image3'] == ['18', 0],
            'latent_still_guide': graph['12']['inputs']['pixels'] == ['4', 0]}


def record(data, start, kind):
    data = first.record(data, start, kind)
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as new:
        for entry in old.infolist():
            value = old.read(entry)
            if entry.filename == 'cycle.json':
                rec = json.loads(value)
                rec['source_sha256'].update({name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                            for name in ('depth_identity_candidate.py', 'depth_identity_alignment.py', 'depth_preprocessing.py')})
                value = json.dumps(rec, indent=2).encode()
            new.writestr(entry.filename, value)
    return output.getvalue()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def reference(source, identity, guide):
    from depth_identity_alignment import run_reference_alignment
    start = time.monotonic()
    return record(run_reference_alignment(source, identity, guide), start, 'identity-first + depth reference')


def motion(payload, archive, guide):
    import cascade_reference_alignment as frozen
    from depth_identity_alignment import run_reference_alignment
    start = time.monotonic(); original = frozen.run_reference_alignment
    try:
        frozen.run_reference_alignment = lambda source, identity: run_reference_alignment(source, identity, guide)
        data = first.previous.baseline.render.local(payload, archive)
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
    names = ('preflight', 'reference', 'video', 'complete')
    saved = {name: getattr(first, name) for name in names}
    try:
        for name in names:
            setattr(first, name, globals()[name])
        first.main(output=output, kind=kind, source=source, identity=identity, guide=guide,
                   cases=cases, case=case, frozen_reference=frozen_reference,
                   budget_directory=budget_directory, confirm_credits_only=confirm_credits_only,
                   usage_observed=usage_observed, remaining_observed=remaining_observed)
    finally:
        for name, value in saved.items():
            setattr(first, name, value)
