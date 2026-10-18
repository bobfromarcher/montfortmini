"""Bounded review/correction/verification cycle; no production endpoint changes."""
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

HERE = Path(__file__).parent
app = modal.App('montfortmini-detail-validation')
image = baseline.image
for name in ('identity_detail.py', 'detail_reference_alignment.py', 'cascade_candidate.py'):
    image = image.add_local_file(HERE / name, '/root/' + name)


@app.function(image=image, cpu=1, memory=512, timeout=60, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    import detail_reference_alignment as detail
    from identity_detail import identity_canvas
    from cascade_reference_alignment import FILES
    return {'imports': callable(detail.refine) and callable(baseline.render.local),
            'real_detail_geometry': identity_canvas(1024, 1536) == (672, 1024),
            'models_present': all((Path('/opt/ComfyUI/models') / item[3]).is_file() for item in FILES)}


def record_execution(data, started, started_utc, kind, placement):
    output = io.BytesIO(data)
    with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as archive:
        record_name = 'candidate.json' if 'candidate.json' in archive.namelist() else 'manifest.json'
        outcome = json.loads(archive.read(record_name))
        archive.writestr('cycle.json', json.dumps({
            'status': outcome['status'], 'failure': outcome.get('failure'),
            'kind': kind, 'placement': placement, 'started_utc': started_utc,
            'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'worker_elapsed_seconds': time.monotonic() - started,
            'source_sha256': {name: hashlib.sha256((Path('/root') / name).read_bytes()).hexdigest()
                              for name in ('detail_cycle.py', 'identity_detail.py', 'detail_reference_alignment.py')}
        }, indent=2))
    return output.getvalue()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def reference(source, identity, placement):
    import detail_reference_alignment as detail
    started = time.monotonic()
    utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data = detail.refine(source, identity) if placement == 'qwen' else detail.cascade(source, identity, 'both')
    return record_execution(data, started, utc, 'reference', placement)


def run_motion(payload, reference_archive, placement):
    import detail_reference_alignment as detail
    import cascade_reference_alignment as frozen
    started = time.monotonic()
    utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    original = frozen.run_reference_alignment
    try:
        frozen.run_reference_alignment = lambda source, identity: detail.cascade(source, identity, placement)
        data = baseline.render.local(payload, reference_archive)
    finally:
        frozen.run_reference_alignment = original
    return record_execution(data, started, utc, 'cached-reference video' if reference_archive else 'fresh full pipeline', placement)


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def video(payload, reference_archive, placement):
    return run_motion(payload, reference_archive, placement)


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def complete(payload, placement):
    return run_motion(payload, None, placement)


@app.local_entrypoint()
def main(output: str, kind: str = 'reference', placement: str = 'qwen',
         source: str = '', identity: str = '', cases: str = '', case: str = '',
         frozen_reference: str = '', control: str = '', confirm_credits_only: bool = False,
         preflight_only: bool = False, ledger: str = 'outputs/adversarial-cycle/gpu-ledger.json'):
    if not confirm_credits_only:
        raise ValueError('Read included credits and $0 cash cap before dispatch')
    if placement not in ('qwen', 'both') or kind not in ('reference', 'video', 'complete'):
        raise ValueError('Unregistered experiment')
    ledger_path = Path(ledger)
    budget = json.loads((ledger_path.parent / 'budget.json').read_text(encoding='utf-8'))
    attempts = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    ceiling = 900 if kind == 'complete' else 660
    committed = sum(item.get('worker_seconds', item['ceiling_seconds']) for item in attempts)
    if len(attempts) >= budget['max_gpu_attempts'] or committed + ceiling > budget['max_worker_seconds']:
        raise RuntimeError('Registered attempt/time budget exhausted; no GPU dispatch')
    check = preflight.remote()
    if not all(check.values()):
        raise RuntimeError('CPU preflight failed; no GPU dispatch')
    print('CPU preflight passed', flush=True)
    if preflight_only:
        Path(output).write_text(json.dumps(check, indent=2), encoding='utf-8')
        return
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=False)
    if kind == 'reference':
        source_bytes, identity_bytes = Path(source).read_bytes(), Path(identity).read_bytes()
        if control:
            old = json.loads((Path(control) / 'manifest.json').read_text(encoding='utf-8'))
            assert hashlib.sha256(source_bytes).hexdigest() == old['source_sha256']
            assert hashlib.sha256(identity_bytes).hexdigest() == old['identity_sha256']
        function, arguments = reference, (source_bytes, identity_bytes, placement)
    else:
        case_file = Path(cases).resolve()
        spec = json.loads(case_file.read_text(encoding='utf-8'))[case]
        payload = {'mode': spec.get('mode', 'motion-transfer'), 'frames': spec['frames'],
                   'seed': spec.get('seed', 42), 'prompt': spec['prompt'],
                   'bbox': spec.get('bbox', [0, 0, 1, 1]), 'end_bbox': spec.get('end_bbox', [0, 0, 1, 1])}
        for field in ('video', 'reference'):
            value = (case_file.parent / spec[field]).read_bytes()
            assert hashlib.sha256(value).hexdigest() == spec['sha256'][field]
            payload[field + '_b64'] = base64.b64encode(value).decode()
        if kind == 'video':
            function, arguments = video, (payload, Path(frozen_reference).read_bytes(), placement)
        else:
            function, arguments = complete, (payload, placement)
    reservation = {'output': str(dest), 'kind': kind, 'placement': placement,
                   'ceiling_seconds': ceiling, 'status': 'reserved',
                   'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    attempts.append(reservation)
    ledger_path.write_text(json.dumps(attempts, indent=2), encoding='utf-8')
    call = function.spawn(*arguments)
    reservation.update(call_id=call.object_id, status='dispatched')
    ledger_path.write_text(json.dumps(attempts, indent=2), encoding='utf-8')
    (dest / 'modal-call.json').write_text(json.dumps(reservation, indent=2), encoding='utf-8')
    print('Modal receipt ' + call.object_id, flush=True)
    data = call.get()
    (dest / 'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if any(not (dest / item.filename).resolve().is_relative_to(dest.resolve()) for item in archive.infolist()):
            raise ValueError('Unsafe evidence path')
        archive.extractall(dest)
    result = json.loads((dest / 'cycle.json').read_text(encoding='utf-8'))
    reservation.update(status=result['status'], worker_seconds=result['worker_elapsed_seconds'])
    ledger_path.write_text(json.dumps(attempts, indent=2), encoding='utf-8')
    print(result['status'], round(result['worker_elapsed_seconds'], 2), flush=True)
    if result['status'] != 'succeeded':
        raise RuntimeError('Technical failure retained; stop before any further GPU attempt')
