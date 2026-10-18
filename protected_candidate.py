"""One reference completion, gated video, then one independent confirmation at most."""
import base64
import datetime
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile
import modal
import cascade_candidate as baseline
from pose_reference_candidate import image as cached_image

HERE = Path(__file__).parent
app = modal.App('montfortmini-protected-completion')
image = (cached_image.add_local_file(HERE / 'protected_reference.py', '/root/protected_reference.py')
         .add_local_file(HERE / 'pose_reference_candidate.py', '/root/pose_reference_candidate.py')
         .add_local_file(HERE / 'protected_candidate.py', '/root/protected_candidate.py'))


@app.function(image=image, cpu=1, memory=512, timeout=60, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    from protected_reference import masked_policy
    from qwen_anchor_workflow import FILES
    return {'import': callable(masked_policy) and (HERE / 'protected_candidate.py').is_file(),
            'models': all((Path('/opt/ComfyUI/models') / item[3]).is_file() for item in FILES)}


def record(data, start, kind):
    output = io.BytesIO(data)
    with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as z:
        name = 'candidate.json' if 'candidate.json' in z.namelist() else 'manifest.json'
        result = json.loads(z.read(name))
        z.writestr('cycle.json', json.dumps({
            'status': result['status'], 'failure': result.get('failure'), 'kind': kind,
            'worker_elapsed_seconds': time.monotonic() - start,
            'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_sha256': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                              for name in ('protected_reference.py', 'protected_candidate.py')}}, indent=2))
    return output.getvalue()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def reference(bundle, identity):
    from protected_reference import run_reference
    start = time.monotonic()
    return record(run_reference(bundle, identity), start, 'protected reference')


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def video(payload, archive):
    start = time.monotonic()
    return record(baseline.render.local(payload, archive), start, 'cached protected-reference video')


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def complete(payload, bundle):
    from protected_reference import run_reference
    start = time.monotonic()
    archive = run_reference(bundle, base64.b64decode(payload['reference_b64']))
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        if json.loads(z.read('manifest.json'))['status'] != 'succeeded':
            return record(archive, start, 'unseen reference failed before video')
    return record(baseline.render.local(payload, archive), start, 'fresh completion plus video')


@app.local_entrypoint()
def main(output: str, kind: str, budget_directory: str, usage_observed: float,
         remaining_observed: float, confirm_credits_only: bool = False,
         bundle: str = '', identity: str = '', cases: str = '', case: str = '',
         frozen_reference: str = ''):
    directory = Path(budget_directory)
    budget = json.loads((directory / 'budget.json').read_text(encoding='utf-8'))
    if not confirm_credits_only or not (0 <= usage_observed < budget['stopping_usage'] and
                                      remaining_observed > budget['stopping_remaining']):
        raise ValueError('Verify live included-credit thresholds and zero cash cap')
    ledger_path = directory / 'gpu-ledger.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    expected = ['reference', 'video', 'complete']
    if len(ledger) >= 3 or kind != expected[len(ledger)]:
        raise ValueError('Exactly one ordered reference/video/independent completion; no rerolls')
    if ledger:
        gate = directory / ('reference-review.json' if kind == 'video' else 'video-review.json')
        if not gate.exists() or json.loads(gate.read_text(encoding='utf-8')).get('gate_pass') is not True:
            raise ValueError('Previous quality gate did not pass; stop')
    if any(entry['status'] != 'succeeded' for entry in ledger):
        raise ValueError('Previous technical failure: stop')
    ceiling = 900 if kind == 'complete' else 660
    if sum(entry['ceiling_seconds'] for entry in ledger) + ceiling > budget['max_worker_seconds']:
        raise ValueError('Worker ceiling exhausted')
    dest = Path(output)
    if dest.exists(): raise ValueError('Preserve earlier evidence; output directory already exists')
    if not all(preflight.remote().values()): raise RuntimeError('CPU preflight failed; no GPU')
    if kind == 'reference':
        function, args = reference, (Path(bundle).read_bytes(), Path(identity).read_bytes())
    else:
        path = Path(cases).resolve(); spec = json.loads(path.read_text(encoding='utf-8'))[case]
        payload = {'mode': 'motion-transfer', 'frames': spec['frames'], 'seed': 42,
                   'prompt': spec['prompt'], 'bbox': [0, 0, 1, 1], 'end_bbox': [0, 0, 1, 1]}
        for field in ('video', 'reference'):
            data = (path.parent / spec[field]).read_bytes()
            if hashlib.sha256(data).hexdigest() != spec['sha256'][field]:
                raise ValueError('Original input hash changed')
            payload[field + '_b64'] = base64.b64encode(data).decode()
        if kind == 'video': function, args = video, (payload, Path(frozen_reference).read_bytes())
        else: function, args = complete, (payload, Path(bundle).read_bytes())
    dest.mkdir(parents=True)
    reservation = {'kind': kind, 'status': 'reserved', 'output': str(dest),
                   'ceiling_seconds': ceiling, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'observed_usage': usage_observed, 'observed_remaining': remaining_observed}
    ledger.append(reservation)
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    call = function.spawn(*args)
    reservation.update(status='dispatched', call_id=call.object_id)
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    (dest / 'modal-call.json').write_text(json.dumps(reservation, indent=2), encoding='utf-8')
    print('Modal receipt ' + call.object_id, flush=True)
    data = call.get(); (dest / 'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest / item.filename).resolve().is_relative_to(dest.resolve()) for item in z.infolist()):
            raise ValueError('Unsafe evidence path')
        z.extractall(dest)
    outcome = json.loads((dest / 'cycle.json').read_text(encoding='utf-8'))
    reservation.update(status=outcome['status'], worker_seconds=outcome['worker_elapsed_seconds'])
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    print(outcome['status'], round(outcome['worker_elapsed_seconds'], 2), flush=True)
    if outcome['status'] != 'succeeded': raise RuntimeError('Failure retained; stop')
