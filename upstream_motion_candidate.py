"""Three-call precision/control diagnostic. Prior failed cycle stays closed."""
import hashlib,io,json,time,zipfile
from pathlib import Path
import modal
import explicit_motion_candidate as baseline
from explicit_motion_workflow import build_graph

HERE=Path(__file__).parent
app=modal.App('montfortmini-upstream-controls')
image=(baseline.image.add_local_file(HERE/'upstream_motion_candidate.py','/root/upstream_motion_candidate.py')
       .add_local_file(HERE/'upstream_motion_controls.py','/root/upstream_motion_controls.py')
       .add_local_dir(HERE/'vendor/wan_animate','/root/vendor/wan_animate'))
cpu_image=(modal.Image.debian_slim(python_version='3.12')
 .uv_pip_install('torch==2.9.1',index_url='https://download.pytorch.org/whl/cpu')
 .uv_pip_install('onnxruntime==1.23.2','matplotlib==3.10.7','opencv-python-headless==4.13.0.92','numpy==2.4.6','Pillow==13.0.0','huggingface_hub==0.36.0')
 .add_local_dir(HERE/'vendor/wan_animate','/root/vendor/wan_animate',copy=True)
 .add_local_file(HERE/'upstream_motion_controls.py','/root/upstream_motion_controls.py',copy=True)
 .run_commands('timeout 900 python /root/upstream_motion_controls.py'))
# Module hydration needs local image-construction dependencies, not their models.
for n in ('upstream_motion_candidate.py','explicit_motion_candidate.py','explicit_motion_workflow.py','motion_probe.py','modal_probe.py','workflow.py','model_config.py','motion_workflow.py','motion_model_config.py','sdk_runner.py','download_models.py','download_motion_models.py','proof_inputs.py','motion_inputs.py','explicit_motion_inputs.py'):
    cpu_image=cpu_image.add_local_file(HERE/n,'/root/'+n)


@app.function(image=cpu_image,cpu=2,memory=16384,timeout=900,max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def controls(inputs):
    from upstream_motion_controls import prepare
    return prepare(inputs)


@app.function(image=image,cpu=1,memory=512,timeout=120,max_containers=1,min_containers=0,scaledown_window=2,retries=0)
def preflight(graph):return baseline.preflight.local(graph)


@app.function(image=image,gpu='L40S',cpu=2,memory=65536,timeout=900,startup_timeout=180,max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def render(inputs,graph):
    import modal_probe
    original=modal_probe.masked_replacement
    class Precision:
        @staticmethod
        def local(graph,info,deadline):return original.local(graph,info,deadline,'bf16')
    modal_probe.masked_replacement=Precision()
    try:data=baseline.render.local(inputs,graph)
    finally:modal_probe.masked_replacement=original
    out=io.BytesIO(data)
    with zipfile.ZipFile(out,'a',zipfile.ZIP_DEFLATED) as z:
        z.writestr('diagnostic-runtime.json',json.dumps({'requested_precision':'bf16','runner_sha256':hashlib.sha256((HERE/'upstream_motion_candidate.py').read_bytes()).hexdigest()},indent=2))
    return out.getvalue()


@app.local_entrypoint()
def main(kind:str,inputs:str,output:str,budget_directory:str,usage_observed:float,remaining_observed:float,confirm_credits_only:bool=False):
    d=Path(budget_directory);budget=json.loads((d/'budget.json').read_text())
    if not confirm_credits_only or not (budget['cash_cap']==0 and usage_observed<budget['stopping_usage'] and remaining_observed>budget['stopping_remaining']):raise ValueError('Credit guard')
    dest=Path(output);dest.mkdir(parents=True,exist_ok=False)
    if kind=='controls':
        data=controls.remote(Path(inputs).read_bytes())
        (dest/'inputs.zip').write_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as z:z.extractall(dest)
        print('CPU controls complete',flush=True);return
    path=d/'gpu-ledger.json';ledger=json.loads(path.read_text()) if path.exists() else []
    if len(ledger)>=3 or any(x['status']!='succeeded' for x in ledger):raise ValueError('Attempt cap/technical stop')
    if kind=='precision':
        if ledger:raise ValueError('Only one precision contrast')
    elif kind=='wholebody':
        if len(ledger)!=1 or json.loads((d/'precision-review.json').read_text()).get('gate_pass') is not False:raise ValueError('Whole-body branch requires failed precision-only quality gate')
    elif kind=='verification':
        if not ledger or any(x['kind']=='verification' for x in ledger):raise ValueError('Only one verification after development')
    else:raise ValueError('Unknown experiment kind')
    if kind=='verification' and not json.loads((d/'candidate-pass.json').read_text()).get('gate_pass'):raise ValueError('No frozen passing candidate')
    frozen=json.loads((d/'candidate-freeze.json').read_text())
    for n,h in frozen['code_sha256'].items():
        if hashlib.sha256((HERE/n).read_bytes()).hexdigest()!=h:raise ValueError('Frozen module changed:'+n)
    input_hash=(json.loads((d/'test-freeze.json').read_text())['input_archive_sha256'] if kind=='verification' else
                json.loads((d/'controls-freeze.json').read_text())['input_archive_sha256'] if kind=='wholebody' else frozen['inputs']['precision'])
    if hashlib.sha256(Path(inputs).read_bytes()).hexdigest()!=input_hash:raise ValueError('Frozen inputs changed')
    graph=build_graph();graph['4']['inputs']['text']=json.loads((d/'control-workflow.json').read_text())['4']['inputs']['text']
    if not all(preflight.remote(graph).values()):raise ValueError('CPU preflight failed')
    row={'kind':kind,'status':'reserved','ceiling_seconds':900,'usage_observed':usage_observed,'remaining_observed':remaining_observed};ledger.append(row);path.write_text(json.dumps(ledger,indent=2))
    call=render.spawn(Path(inputs).read_bytes(),graph);row.update(status='dispatched',call_id=call.object_id);path.write_text(json.dumps(ledger,indent=2));(dest/'modal-call.json').write_text(json.dumps(row,indent=2));print('Modal call receipt:'+call.object_id,flush=True)
    data=call.get();(dest/'evidence.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):raise ValueError('Unsafe archive')
        z.extractall(dest)
    record=json.loads((dest/'candidate.json').read_text());row.update(status=record['status'],worker_elapsed_seconds=record['worker_elapsed_seconds']);path.write_text(json.dumps(ledger,indent=2))
    print(record['status'],round(record['worker_elapsed_seconds'],2),flush=True)
    if record['failure']:raise RuntimeError('Technical failure; stop')
