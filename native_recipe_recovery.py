"""Single technical recovery of a frozen, previously unscored recording.

This has its own one-attempt ledger; it never reopens the closed diagnostic.
The fixture, graph, acceptance events and runtime sources must be frozen first.
"""
import datetime
import hashlib
import io
import json
from pathlib import Path
import zipfile

import modal
import native_recipe_candidate as candidate
from native_recipe_fixture import validate_fixture
from native_recipe_workflow import build_graph

HERE = Path(__file__).parent
app = modal.App('montfortmini-native-recovery')
image = candidate.image.add_local_file(HERE / 'native_recipe_recovery.py',
                                       '/root/native_recipe_recovery.py')


@app.function(image=image, cpu=1, memory=512, timeout=120, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    return candidate.preflight.local()


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def render(inputs, graph):
    data = candidate.render.local(inputs, graph)
    stream = io.BytesIO(data)
    with zipfile.ZipFile(stream, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('recovery-runtime.json', json.dumps({
            'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope': 'Corrected mask-file packaging only; previously unscored recording.'}, indent=2))
    return stream.getvalue()


def verify_local(directory, usage, remaining):
    frozen = json.loads((directory / 'freeze.json').read_text(encoding='utf-8'))
    budget = frozen['budget']
    if not (budget['cash_cap'] == 0 and budget['included_cap'] == 1 and
            budget['max_gpu_attempts'] == 1 and budget['max_worker_seconds'] == 900 and
            usage < budget['stopping_usage'] and remaining > budget['stopping_remaining']):
        raise ValueError('Included-credit guard')
    ledger_path = directory / 'gpu-ledger.json'
    if ledger_path.exists() and json.loads(ledger_path.read_text(encoding='utf-8')):
        raise ValueError('Recovery already reserved; no automatic retry')
    for name, digest in frozen['source_sha256'].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen source changed: ' + name)
    for name, digest in frozen['artifact_sha256'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen artifact changed: ' + name)
    graph = build_graph()
    if graph != frozen['graph']:
        raise ValueError('Graph differs from passing candidate')
    payload = (directory / 'inputs.zip').read_bytes()
    shape = graph['7']['inputs']
    validation = validate_fixture(payload, frames=shape['length'],
                                  width=shape['width'], height=shape['height'])
    return frozen, payload, graph, validation


@app.local_entrypoint()
def main(directory: str, usage_observed: float, remaining_observed: float,
         confirm_credits_only: bool = False):
    if not confirm_credits_only:
        raise ValueError('Live billing and $0 cash limit must be checked first')
    root = Path(directory)
    frozen, payload, graph, validation = verify_local(root, usage_observed, remaining_observed)
    (root / 'fixture-validation.json').write_text(json.dumps(validation, indent=2))
    check = preflight.remote()
    (root / 'preflight.json').write_text(json.dumps(check, indent=2))
    if not check or not all(check.values()):
        raise ValueError('CPU preflight failed; no GPU reserved')
    dest = root / 'result'
    dest.mkdir(exist_ok=False)
    row = {'status': 'reserved', 'ceiling_seconds': 900,
           'reserved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'usage_observed': usage_observed, 'remaining_observed': remaining_observed,
           'freeze_sha256': hashlib.sha256((root / 'freeze.json').read_bytes()).hexdigest()}
    ledger = root / 'gpu-ledger.json'
    ledger.write_text(json.dumps([row], indent=2))
    try:
        call = render.spawn(payload, graph)
        row.update(status='dispatched', call_id=call.object_id)
        ledger.write_text(json.dumps([row], indent=2))
        (dest / 'modal-call.json').write_text(json.dumps(row, indent=2))
        print('Modal call receipt: ' + call.object_id, flush=True)
        data = call.get()
        (dest / 'evidence.zip').write_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if any(not (dest / item.filename).resolve().is_relative_to(dest.resolve())
                   for item in archive.infolist()):
                raise ValueError('Unsafe result archive')
            archive.extractall(dest)
        record = json.loads((dest / 'candidate.json').read_text(encoding='utf-8'))
        row.update(status=record['status'], worker_elapsed_seconds=record['worker_elapsed_seconds'])
        if record['failure']:
            raise RuntimeError('Worker failed; recovery closed')
        print('succeeded ' + str(round(record['worker_elapsed_seconds'], 2)), flush=True)
    except Exception as exc:
        row.update(status='failed', exception_type=type(exc).__name__)
        raise
    finally:
        ledger.write_text(json.dumps([row], indent=2))
