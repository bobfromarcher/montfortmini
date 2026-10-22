"""Bounded alternative reference path. Existing production/video graph remains frozen."""
import base64
import datetime
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path
import modal
import cascade_candidate as baseline
from detail_cycle import image as cached_image

HERE = Path(__file__).parent
app = modal.App('montfortmini-pose-reference')
image = (cached_image
         .add_local_file(HERE / 'detail_cycle.py', '/root/detail_cycle.py')
         .add_local_file(HERE / 'pose_reference_alignment.py', '/root/pose_reference_alignment.py'))


@app.function(image=image, cpu=1, memory=512, timeout=60, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    from pose_reference_alignment import run_reference_alignment
    from qwen_anchor_workflow import FILES
    return {'imports': callable(run_reference_alignment),
            'models': all((Path('/opt/ComfyUI/models') / f[3]).is_file() for f in FILES)}


def record(data, start, kind):
    stream = io.BytesIO(data)
    with zipfile.ZipFile(stream, 'a', zipfile.ZIP_DEFLATED) as z:
        name = 'candidate.json' if 'candidate.json' in z.namelist() else 'manifest.json'
        manifest = json.loads(z.read(name))
        z.writestr('cycle.json', json.dumps({
            'status': manifest['status'], 'failure': manifest.get('failure'),
            'kind': kind, 'worker_elapsed_seconds': time.monotonic() - start,
            'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_sha256': {name: hashlib.sha256((Path('/root') / name).read_bytes()).hexdigest()
                              for name in ('pose_reference_candidate.py', 'pose_reference_alignment.py',
                                           'identity_detail.py', 'detail_reference_alignment.py')}
        }, indent=2))
    return stream.getvalue()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def reference(source, identity, guide):
    from pose_reference_alignment import run_reference_alignment
    start = time.monotonic()
    return record(run_reference_alignment(source, identity, guide), start, 'reference')


def motion(payload, archive, guide):
    import cascade_reference_alignment as frozen
    from pose_reference_alignment import run_reference_alignment
    start = time.monotonic()
    original = frozen.run_reference_alignment
    try:
        frozen.run_reference_alignment = lambda source, identity: run_reference_alignment(source, identity, guide)
        data = baseline.render.local(payload, archive)
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
         budget_directory: str = 'outputs/pose-reference', confirm_credits_only: bool = False,
         usage_observed: float = -1, remaining_observed: float = -1):
    if not confirm_credits_only or kind not in ('reference', 'video', 'complete'):
        raise ValueError('Read declared budget, included credits and $0 cash cap; choose a registered kind')
    directory = Path(budget_directory)
    budget = json.loads((directory / 'budget.json').read_text(encoding='utf-8'))
    if not (0 <= usage_observed < budget['stopping_usage'] and remaining_observed > budget['stopping_remaining']):
        raise ValueError('Missing/reached observed credit threshold; do not dispatch')
    ledger_path = directory / 'gpu-ledger.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    ceiling = 900 if kind == 'complete' else 660
    # Reserve full ceilings, including successful calls, so timing cannot expand the plan.
    if (len(ledger) >= budget['max_gpu_attempts'] or
        sum(x['ceiling_seconds'] for x in ledger) + ceiling > budget['max_worker_seconds'] or
        any(x['status'] not in ('succeeded',) for x in ledger)):
        raise RuntimeError('Attempt/time/technical-failure stopping rule reached')
    if kind == 'reference' and (len(ledger) >= 2 or
        sum(x['ceiling_seconds'] for x in ledger) + ceiling + budget['reserved_verification_worker_seconds'] > budget['max_worker_seconds']):
        raise RuntimeError('Reference call would consume reserved verification budget')
    check = preflight.remote()
    if not all(check.values()):
        raise RuntimeError('CPU preflight failed; no GPU')
    print('CPU preflight passed', flush=True)
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=False)
    if kind == 'reference':
        function, args = reference, (Path(source).read_bytes(), Path(identity).read_bytes(), Path(guide).read_bytes())
    else:
        path = Path(cases).resolve()
        spec = json.loads(path.read_text(encoding='utf-8'))[case]
        payload = {'mode': 'motion-transfer', 'frames': spec['frames'], 'seed': 42,
                   'prompt': spec['prompt'], 'bbox': [0, 0, 1, 1], 'end_bbox': [0, 0, 1, 1]}
        for field in ('video', 'reference'):
            data = (path.parent / spec[field]).read_bytes()
            if hashlib.sha256(data).hexdigest() != spec['sha256'][field]:
                raise ValueError('Original input hash changed')
            payload[field + '_b64'] = base64.b64encode(data).decode()
        function, args = ((video, (payload, Path(frozen_reference).read_bytes())) if kind == 'video'
                          else (complete, (payload, Path(guide).read_bytes())))
    reservation = {'output': str(dest), 'kind': kind, 'status': 'reserved',
                   'ceiling_seconds': ceiling, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'observed_usage': usage_observed, 'observed_remaining': remaining_observed}
    ledger.append(reservation)
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    call = function.spawn(*args)
    reservation.update(call_id=call.object_id, status='dispatched')
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    (dest / 'modal-call.json').write_text(json.dumps(reservation, indent=2), encoding='utf-8')
    print('Modal receipt ' + call.object_id, flush=True)
    data = call.get()
    (dest / 'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest / i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):
            raise ValueError('Unsafe archive')
        z.extractall(dest)
    outcome = json.loads((dest / 'cycle.json').read_text(encoding='utf-8'))
    reservation.update(status=outcome['status'], worker_seconds=outcome['worker_elapsed_seconds'])
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    print(outcome['status'], round(outcome['worker_elapsed_seconds'], 2), flush=True)
    if outcome['status'] != 'succeeded':
        raise RuntimeError('Technical failure retained; stop')
