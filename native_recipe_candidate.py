"""One closed diagnostic branch: oracle, reference, then gated verification."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
import modal
import explicit_motion_candidate as prior
from motion_probe import motion_base_image
from native_recipe_models import ASSETS
from native_recipe_workflow import build_graph
from native_recipe_fixture import validate_fixture

HERE = Path(__file__).parent
app = modal.App('montfortmini-native-recipe')
image = (motion_base_image
         .add_local_file(HERE/'native_recipe_models.py', '/root/native_recipe_models.py', copy=True)
         .run_commands('timeout 900 python /root/native_recipe_models.py'))
NAMES = ('native_recipe_candidate.py', 'native_recipe_workflow.py', 'native_recipe_models.py',
         'native_recipe_fixture.py',
         'explicit_motion_candidate.py', 'explicit_motion_workflow.py', 'explicit_motion_inputs.py',
         'workflow.py', 'model_config.py', 'motion_probe.py', 'modal_probe.py', 'motion_workflow.py',
         'motion_model_config.py', 'sdk_runner.py', 'download_models.py', 'download_motion_models.py',
         'proof_inputs.py', 'motion_inputs.py')
for name in NAMES:
    image = image.add_local_file(HERE/name, '/root/'+name)
image = image.add_local_file(HERE/'explicit_motion_inputs.py',
                             '/opt/ComfyUI/custom_nodes/explicit_motion_inputs.py')


@app.function(image=image, cpu=1, memory=512, timeout=120, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def preflight():
    return {a['file']: (Path('/opt/ComfyUI/models')/a['directory']/Path(a['file']).name).stat().st_size == a['bytes']
            for a in ASSETS}


@app.function(image=image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def render(inputs, graph):
    import modal_probe
    original = modal_probe.masked_replacement

    class NativeRecipe:
        @staticmethod
        def local(graph, info, deadline):
            info.update(repo=ASSETS[0]['repo'], revision=ASSETS[0]['revision'],
                        input_provenance='Frozen development media; see recipe-runtime.json for oracle/reference role')
            return original.local(graph, info, deadline, 'auto')

    modal_probe.masked_replacement = NativeRecipe()
    try:
        data = prior.render.local(inputs, graph)
    finally:
        modal_probe.masked_replacement = original
    result = io.BytesIO(data)
    with zipfile.ZipFile(result, 'a', zipfile.ZIP_DEFLATED) as z:
        # Preserve available inference images even if downstream compositing or
        # packaging failed; an ephemeral worker cannot be recovered after exit.
        record = json.loads(z.read('candidate.json'))
        if record['failure']:
            for folder, label in ((Path('/tmp/openjutsu-result'), 'result'),
                                  (Path('/tmp/openjutsu-sdk-output'), 'sdk')):
                if folder.exists():
                    for path in sorted(folder.rglob('*')):
                        if path.is_file() and path.suffix.lower() in ('.png', '.mp4', '.json', '.log'):
                            z.write(path, 'failure/recovered-'+label+'/'+path.relative_to(folder).as_posix())
        z.writestr('recipe-runtime.json', json.dumps({'assets': ASSETS,
            'code_sha256': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in NAMES},
            'precision': 'auto', 'production_default_changed': False}, indent=2))
    return result.getvalue()


@app.local_entrypoint()
def main(kind: str, inputs: str, output: str, budget_directory: str,
         usage_observed: float, remaining_observed: float, confirm_credits_only: bool = False):
    directory = Path(budget_directory)
    budget = json.loads((directory/'budget.json').read_text())
    if not confirm_credits_only or budget['cash_cap'] != 0 or not (
            usage_observed < budget['stopping_usage'] and remaining_observed > budget['stopping_remaining']):
        raise ValueError('Included credit guard')
    path = directory/'gpu-ledger.json'
    ledger = json.loads(path.read_text()) if path.exists() else []
    if len(ledger) >= 3 or any(r['status'] != 'succeeded' for r in ledger):
        raise ValueError('Attempt cap or prior technical failure')
    expected = ('oracle', 'reference', 'verification')[len(ledger)]
    if kind != expected:
        raise ValueError('Diagnostic order must be oracle -> reference -> verification')
    if ledger and json.loads((directory/(ledger[-1]['kind']+'-review.json')).read_text()).get('gate_pass') is not True:
        raise ValueError('Previous quality gate did not pass')
    frozen = json.loads((directory/'candidate-freeze.json').read_text())
    for name, digest in frozen['code_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen source changed: '+name)
    if kind == 'verification':
        gate = json.loads((directory/'candidate-pass.json').read_text())
        if gate.get('gate_pass') is not True:
            raise ValueError('Candidate is not frozen as passing')
        input_hash = json.loads((directory/'test-freeze.json').read_text())['input_archive_sha256']
    else:
        input_hash = frozen['inputs'][kind]
    payload = Path(inputs).read_bytes()
    if hashlib.sha256(payload).hexdigest() != input_hash:
        raise ValueError('Input archive changed')
    graph = build_graph()
    if graph != frozen['graph']:
        raise ValueError('Frozen graph changed')
    shape = graph['7']['inputs']
    validate_fixture(payload, frames=shape['length'], width=shape['width'], height=shape['height'])
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=False)
    check = preflight.remote()
    (directory/'preflight.json').write_text(json.dumps(check, indent=2))
    if not all(check.values()):
        raise ValueError('CPU model preflight failed; no GPU reservation')
    row = {'kind': kind, 'status': 'reserved', 'ceiling_seconds': 900,
           'usage_observed': usage_observed, 'remaining_observed': remaining_observed}
    ledger.append(row)
    path.write_text(json.dumps(ledger, indent=2))
    call = render.spawn(payload, graph)
    row.update(status='dispatched', call_id=call.object_id)
    path.write_text(json.dumps(ledger, indent=2))
    (dest/'modal-call.json').write_text(json.dumps(row, indent=2))
    print('Modal call receipt: '+call.object_id, flush=True)
    data = call.get()
    (dest/'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):
            raise ValueError('Unsafe archive')
        z.extractall(dest)
    record = json.loads((dest/'candidate.json').read_text())
    row.update(status=record['status'], worker_elapsed_seconds=record['worker_elapsed_seconds'])
    path.write_text(json.dumps(ledger, indent=2))
    print(record['status'], round(record['worker_elapsed_seconds'], 2), flush=True)
    if record['failure']:
        raise RuntimeError('Technical failure; diagnostic stopped')
