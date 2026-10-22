"""Bounded private explicit-motion experiment. No endpoint or production change."""
import datetime
import hashlib
import io
import json
from pathlib import Path
import threading
import time
import zipfile
import modal
from motion_probe import motion_base_image

HERE=Path(__file__).parent
app=modal.App('montfortmini-explicit-motion')
image=(motion_base_image
       .add_local_file(HERE/'explicit_motion_workflow.py','/root/explicit_motion_workflow.py',copy=True)
       .add_local_file(HERE/'workflow.py','/root/workflow.py',copy=True)
       .run_commands('timeout 1200 python /root/explicit_motion_workflow.py'))
for name in ('model_config.py','sdk_runner.py','modal_probe.py','explicit_motion_candidate.py',
             'motion_probe.py','motion_workflow.py','motion_model_config.py',
             'download_models.py','download_motion_models.py','proof_inputs.py','motion_inputs.py'):
    image=image.add_local_file(HERE/name,'/root/'+name)
image=image.add_local_file(HERE/'explicit_motion_inputs.py','/opt/ComfyUI/custom_nodes/explicit_motion_inputs.py')


def resource_sample(gpu_reader,memory_path):
    """A missing cgroup reading must not discard a valid GPU measurement."""
    gpu=gpu_reader().strip()
    try:
        memory=memory_path.read_text().strip()
        error=None
    except Exception as exc:
        memory='';error={'stage':'cgroup-memory','type':type(exc).__name__,'message':str(exc)}
    return gpu+','+memory,error


@app.function(image=image,cpu=1,memory=512,timeout=120,max_containers=1,
              min_containers=0,scaledown_window=2,retries=0)
def preflight(graph):
    from explicit_motion_workflow import MODEL_FILE,MODEL_BYTES
    path=Path('/opt/ComfyUI/models/diffusion_models')/MODEL_FILE
    source=Path('/opt/ComfyUI/comfy_extras/nodes_wan.py').read_text()
    return {'model_size':path.is_file() and path.stat().st_size==MODEL_BYTES,
            'native_node':'class WanAnimateToVideo(' in source,
            'explicit_inputs':Path('/opt/ComfyUI/custom_nodes/explicit_motion_inputs.py').is_file(),
            'graph_node':graph['7']['class_type']=='WanAnimateToVideo'}


@app.function(image=image,gpu='L40S',cpu=2,memory=65536,timeout=900,
              startup_timeout=180,max_containers=1,min_containers=0,
              scaledown_window=2,retries=0,single_use_containers=True)
def render(inputs,graph):
    import subprocess
    from explicit_motion_workflow import MODEL_REPO,MODEL_REVISION
    from modal_probe import masked_replacement
    start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    fixture=Path('/tmp/openjutsu-fixture');fixture.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(inputs)) as z:
        if any(not (fixture/i.filename).resolve().is_relative_to(fixture) for i in z.infolist()):
            raise ValueError('Unsafe input archive')
        z.extractall(fixture)
    samples=[];monitor_errors=[];stop=threading.Event()
    def monitor():
        while not stop.is_set():
            try:
                line,error=resource_sample(lambda:subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,utilization.gpu,memory.used,power.draw',
                    '--format=csv,noheader,nounits'],text=True,timeout=5),Path('/sys/fs/cgroup/memory.current'))
                samples.append(line)
                if error:monitor_errors.append(error)
            except Exception as exc:monitor_errors.append({'stage':'gpu-monitor','type':type(exc).__name__,'message':str(exc)})
            stop.wait(1)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    failure=None;data=b''
    try:
        data=masked_replacement.local(graph,{'repo':MODEL_REPO,'revision':MODEL_REVISION,
            'mode':'motion-transfer','input_provenance':'same CC0 development frames and protected fictional-reference pixels'},840)
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    finally:stop.set();thread.join(timeout=6)
    result=io.BytesIO(data)
    with zipfile.ZipFile(result,'a',zipfile.ZIP_DEFLATED) as z:
        z.writestr('candidate.json',json.dumps({'status':'failed' if failure else 'succeeded','failure':failure,
            'started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'worker_elapsed_seconds':time.monotonic()-start,'input_archive_sha256':hashlib.sha256(inputs).hexdigest(),
            'monitor_sample_count':len(samples),'monitor_errors':monitor_errors,
            'source_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                             for name in ('explicit_motion_workflow.py','explicit_motion_candidate.py','modal_probe.py','sdk_runner.py')}
            },indent=2))
        z.writestr('candidate-gpu.csv','timestamp,utilization_percent,memory_MiB,power_W,cgroup_memory_current_bytes\n'+'\n'.join(samples))
        if failure:
            z.writestr('workflow-api.json',json.dumps(graph,indent=2))
            for path in (Path('/tmp/comfy.log'),Path('/tmp/openjutsu-sdk-output/job-receipt.json')):
                if path.exists():z.writestr('failure/'+path.name,path.read_bytes())
    return result.getvalue()


def authorize_attempt(directory,kind,usage,remaining):
    budget=json.loads((directory/'budget.json').read_text())
    path=directory/'gpu-ledger.json'
    ledger=json.loads(path.read_text()) if path.exists() else []
    if not (budget['cash_cap']==0 and usage<budget['stopping_usage'] and remaining>budget['stopping_remaining']):
        raise ValueError('Included credit thresholds exhausted')
    if len(ledger)>=budget['max_gpu_attempts'] or any(x['status']!='succeeded' for x in ledger):
        raise ValueError('Attempt cap or previous technical failure')
    if kind=='development':
        if ledger:raise ValueError('Only one development generation')
    elif kind in ('face-off','verification'):
        gate=json.loads((directory/'development-review.json').read_text())
        if kind=='face-off':
            if len(ledger)!=1 or not gate.get('motion_pass') or not gate.get('identity_leak_demonstrated'):
                raise ValueError('Face ablation requires passing motion and demonstrated source-identity leak')
        elif not (directory/'candidate-pass.json').exists() or json.loads((directory/'candidate-pass.json').read_text()).get('gate_pass') is not True:raise ValueError('No frozen passing candidate')
        elif any(x['kind']=='verification' for x in ledger):raise ValueError('Only one unseen verification')
    else:raise ValueError('Unknown experiment kind')
    if sum(x['ceiling_seconds'] for x in ledger)+900>budget['max_worker_seconds']:
        raise ValueError('Worker ceiling exhausted')
    return ledger,path


@app.local_entrypoint()
def main(inputs:str,output:str,budget_directory:str,usage_observed:float,remaining_observed:float,
         kind:str='development',confirm_credits_only:bool=False,preflight_only:bool=False):
    if not confirm_credits_only:raise ValueError('Verify credits and zero cash cap before running')
    from explicit_motion_workflow import build_graph
    directory=Path(budget_directory)
    ledger,ledger_path=authorize_attempt(directory,kind,usage_observed,remaining_observed)
    cfg=json.loads(zipfile.ZipFile(inputs).read('settings.json'))
    graph=build_graph(cfg['width'],cfg['height'],cfg['frames'],face=kind!='face-off')
    # Keep the appearance prompt identical to the retained control in this study.
    graph['4']['inputs']['text']=json.loads((directory/'control-workflow.json').read_text())['4']['inputs']['text']
    check=preflight.remote(graph)
    print('CPU preflight '+json.dumps(check),flush=True)
    (directory/'preflight.json').write_text(json.dumps(check,indent=2))
    if not all(check.values()):raise RuntimeError('CPU preflight failed; no GPU')
    if preflight_only:return
    frozen=json.loads((directory/'candidate-freeze.json').read_text())
    for name,digest in frozen['code_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen code changed: '+name)
    if kind=='development' and hashlib.sha256(Path(inputs).read_bytes()).hexdigest()!=frozen['input_archive_sha256']:
        raise ValueError('Frozen input archive changed')
    dest=Path(output);dest.mkdir(parents=True,exist_ok=False)
    reservation={'kind':kind,'status':'reserved','ceiling_seconds':900,'usage_observed':usage_observed,
                 'remaining_observed':remaining_observed,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    ledger.append(reservation);ledger_path.write_text(json.dumps(ledger,indent=2))
    call=render.spawn(Path(inputs).read_bytes(),graph)
    reservation.update(status='dispatched',call_id=call.object_id)
    ledger_path.write_text(json.dumps(ledger,indent=2))
    (dest/'modal-call.json').write_text(json.dumps(reservation,indent=2))
    print('Modal call receipt: '+call.object_id,flush=True)
    data=call.get();(dest/'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):raise ValueError('Unsafe result archive')
        z.extractall(dest)
    record=json.loads((dest/'candidate.json').read_text())
    reservation.update(status=record['status'],worker_elapsed_seconds=record['worker_elapsed_seconds'])
    ledger_path.write_text(json.dumps(ledger,indent=2))
    print(record['status'],round(record['worker_elapsed_seconds'],2),flush=True)
    if record['failure']:raise RuntimeError('GPU call failed; no automatic retry')
