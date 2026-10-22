"""Final source-luma plus descriptive-prompt diagnostic; no production change."""
from pathlib import Path
import hashlib
import io
import json
import zipfile

import modal
import service
import explicit_motion_candidate as runner
import model_config

HERE = Path(__file__).parent
app = modal.App('montfortmini-object-luminance-prompt')
NAMES = tuple(dict.fromkeys((*service.native_motion_backend.SOURCE_NAMES,
                            'service.py', 'legacy_local_inference.py', 'object_luminance_prompt_candidate.py', 'object_luminance_inputs.py')))
image = service.gpu_image.add_local_file(HERE/'service.py', '/root/service.py')
image = image.add_local_file(HERE/'object_luminance_prompt_candidate.py', '/root/object_luminance_prompt_candidate.py')
image = image.add_local_file(HERE/'object_luminance_inputs.py', '/root/object_luminance_inputs.py')
image = image.add_local_file(HERE/'object_luminance_inputs.py', '/opt/ComfyUI/custom_nodes/openjutsu_luminance.py')


@app.function(image=image, gpu='L40S', cpu=2, memory=32768, timeout=660,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def render(inputs, graph):
    import modal_probe
    original = modal_probe.masked_replacement

    class ObjectRecipe:
        @staticmethod
        def local(graph, info, deadline, precision='auto'):
            info.update(repo=model_config.MODEL_REPO, revision=model_config.MODEL_REVISION,
                        mode='object-swap', input_provenance='Retained CC-BY development recording; original reference/wide masks; source luma plus retained output-description prompt')
            return original.local(graph, info, min(deadline, 560), precision)

    modal_probe.masked_replacement = ObjectRecipe()
    try:
        data = runner.render.local(inputs, graph)
    finally:
        modal_probe.masked_replacement = original
    stream = io.BytesIO(data)
    with zipfile.ZipFile(stream, 'a', zipfile.ZIP_DEFLATED) as archive:
        record = json.loads(archive.read('candidate.json'))
        if record['failure']:
            for folder,label in ((Path('/tmp/openjutsu-result'),'result'),(Path('/tmp/openjutsu-sdk-output'),'sdk')):
                if folder.exists():
                    for path in sorted(folder.rglob('*')):
                        if path.is_file() and path.suffix.lower() in ('.png','.mp4','.json','.log'):
                            archive.write(path,'failure/recovered-'+label+'/'+path.relative_to(folder).as_posix())
        archive.writestr('object-runtime.json', json.dumps({
            'source_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in NAMES},
            'model_repo':model_config.MODEL_REPO,'model_revision':model_config.MODEL_REVISION,
            'intervention':'Paired against source-luma-only candidate: positive prompt changes to the retained output description. Against original baseline, control node6 and positive prompt4 change. Source RGB, reference, masks, seed and sampling stay fixed; executed tensors retained.'},indent=2))
    return stream.getvalue()


@app.local_entrypoint()
def main(directory: str, confirm_credits_only: bool = False):
    root=Path(directory)
    freeze=json.loads((root/'freeze.json').read_text(encoding='utf-8'))
    if not confirm_credits_only or freeze['budget']['cash_cap']!=0 or freeze['budget']['included_cap']!=.75:
        raise ValueError('Live credits-only check and $0.75 one-attempt cap required')
    ledger=root/'gpu-ledger.json'
    if ledger.exists():raise ValueError('Attempt already reserved; no retry')
    for name,digest in freeze['source_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Source changed: '+name)
    for name,digest in freeze['artifact_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('Input changed: '+name)
    payload=(root/'inputs.zip').read_bytes();graph=json.loads((root/'control-workflow.json').read_text())
    shape=graph['7']['inputs']
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        required={'settings.json','reference.png','conditioning.npz'}|{f'{folder}/{i:04d}.png' for folder in ('source','masks') for i in range(shape['length'])}
        if not required.issubset(archive.namelist()):raise ValueError('Incomplete postprocessing fixture')
    row={'status':'reserved','max_gpu_calls':1,'max_gpu_seconds':660};ledger.write_text(json.dumps([row],indent=2))
    try:
        call=render.spawn(payload,graph);row.update(status='dispatched',call_id=call.object_id);ledger.write_text(json.dumps([row],indent=2));print('Luma plus descriptive-prompt diagnostic receipt: '+call.object_id,flush=True)
        data=call.get();dest=root/'result';dest.mkdir(exist_ok=False);(dest/'evidence.zip').write_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in archive.infolist()):raise ValueError('Unsafe archive')
            archive.extractall(dest)
        record=json.loads((dest/'candidate.json').read_text());row.update(status=record['status'],worker_seconds=record['worker_elapsed_seconds'])
        if record['failure']:raise RuntimeError('Technical failure; stop')
        print('Luma plus descriptive-prompt diagnostic completed',flush=True)
    except Exception as exc:
        row.update(status='failed',exception_type=type(exc).__name__);raise
    finally:ledger.write_text(json.dumps([row],indent=2))
