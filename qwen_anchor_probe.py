"""Bounded, private, official-SDK experiment. No production/UI feature added."""
import base64,datetime,hashlib,io,json,time,zipfile
from pathlib import Path
import modal
from modal_probe import base_image
from qwen_anchor_workflow import build_graph,FILES,PROMPT
HERE=Path(__file__).parent
app=modal.App('montfortmini-qwen-reference-comparison')
image=(base_image.add_local_file(HERE/'qwen_anchor_workflow.py','/root/qwen_anchor_workflow.py',copy=True)
 .run_commands('timeout 900 python /root/qwen_anchor_workflow.py')
 .add_local_file(HERE/'modal_probe.py','/root/modal_probe.py')
 .add_local_file(HERE/'proof_inputs.py','/root/proof_inputs.py')
 .add_local_file(HERE/'sdk_runner.py','/root/sdk_runner.py')
 .add_local_file(HERE/'workflow.py','/root/workflow.py')
 .add_local_file(HERE/'reference_alignment.py','/root/reference_alignment.py')
 .add_local_file(HERE/'anchor_workflow.py','/root/anchor_workflow.py'))
@app.function(image=image,cpu=1,memory=2048,timeout=120,max_containers=1,min_containers=0,scaledown_window=2,retries=0)
def preflight():
 """Validate worker imports and native graph contract before allocating a GPU."""
 import subprocess
 from urllib.request import urlopen
 from workflow import validate_graph
 from sdk_runner import run_with_sdk
 proc=subprocess.Popen(['python','main.py','--cpu','--listen','127.0.0.1','--port','8188','--disable-auto-launch','--preview-method','none'],cwd='/opt/ComfyUI',stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
 try:
  deadline=time.monotonic()+90
  while True:
   try:
    with urlopen('http://127.0.0.1:8188/object_info',timeout=5) as r:schema=json.load(r)
    break
   except OSError:
    if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('CPU graph preflight startup failed')
    time.sleep(1)
  graph=build_graph();validate_graph(graph,schema)
  return {'status':'passed','graph_classes':sorted({v['class_type'] for v in graph.values()}),'model_files_present':all((Path('/opt/ComfyUI/models')/f[3]).is_file() for f in FILES)}
 finally:
  proc.terminate()
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
@app.function(image=image,gpu='L40S',cpu=2,memory=65536,timeout=660,startup_timeout=180,
 max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def prepare(source,identity,prompt,full_reference_resolution=False):
 import subprocess,threading,psutil
 from urllib.request import urlopen
 from PIL import Image,ImageOps
 from workflow import validate_graph
 from sdk_runner import run_with_sdk
 start=time.monotonic();started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat();root=Path('/tmp/anchor-evidence');root.mkdir(exist_ok=True)
 target=Path('/opt/ComfyUI/input');target.mkdir(exist_ok=True)
 for name,data,size in [('source',source,(768,1360)),('identity',identity,None)]:
  (root/(name+'-original.png')).write_bytes(data)
  with Image.open(io.BytesIO(data)) as im:
   im=ImageOps.exif_transpose(im).convert('RGB')
   if size:im=im.resize(size,Image.Resampling.LANCZOS)
   else:
    im=im.resize((512,480),Image.Resampling.LANCZOS)
    if full_reference_resolution:im=im.resize((1024,960),Image.Resampling.NEAREST)
   im.save(target/('recovery-'+name+'.png'));im.save(root/(name+'-conditioning.png'))
 graph=build_graph(prompt);(root/'workflow-api.json').write_text(json.dumps(graph,indent=2),encoding='utf-8')
 log=(root/'comfy.log').open('w',encoding='utf-8');proc=None;proxy=None;failure=None;receipt=None;samples=[];stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:samples.append(subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],text=True,timeout=5).strip())
   except Exception:pass
   stop.wait(1)
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 try:
  proc=subprocess.Popen(['python','main.py','--listen','127.0.0.1','--port','8188','--disable-auto-launch','--preview-method','none'],cwd='/opt/ComfyUI',stdout=log,stderr=subprocess.STDOUT)
  while True:
   try:
    with urlopen('http://127.0.0.1:8188/object_info',timeout=5) as r:schema=json.load(r)
    break
   except OSError:
    if proc.poll() is not None or time.monotonic()-start>90:raise RuntimeError('Comfy startup failure')
    time.sleep(1)
  validate_graph(graph,schema)
  (root/'node-schema.json').write_text(json.dumps({v['class_type']:schema[v['class_type']] for v in graph.values()},indent=2),encoding='utf-8')
  proxy=subprocess.Popen(['comfy-api-proxy','--comfyui','http://127.0.0.1:8188','--port','8189'],stdout=log,stderr=subprocess.STDOUT)
  for _ in range(80):
   try:
    with urlopen('http://127.0.0.1:8189/api/v2/health',timeout=2) as r:
     if r.status==200:break
   except OSError:pass
   time.sleep(.25)
  receipt=run_with_sdk(graph,'/tmp/anchor-sdk',timeout=480)
  raw=[Path(f) for f in receipt['files'] if str(f).endswith('.png')]
  if len(raw)!=1:raise RuntimeError('Expected exactly one reference image')
  (root/'anchor.png').write_bytes(raw[0].read_bytes())
 except Exception as e:failure={'type':type(e).__name__,'message':str(e)}
 finally:
  stop.set();thread.join(timeout=6)
  for p in (proxy,proc):
   if p:
    p.terminate()
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
  log.close()
 (root/'gpu.csv').write_text('timestamp,utilization_percent,memory_MiB,power_W\n'+'\n'.join(samples),encoding='utf-8')
 metadata={'status':'failed' if failure else 'succeeded','failure':failure,'worker_elapsed_seconds':time.monotonic()-start,'sdk_receipt':receipt,'models':FILES,'prompt':prompt,'seed':42,'started_utc':started_utc,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_reference_resolution':full_reference_resolution,'source_sha256':hashlib.sha256(source).hexdigest(),'identity_sha256':hashlib.sha256(identity).hexdigest(),'software_sha256':{n:hashlib.sha256((Path('/root')/n).read_bytes()).hexdigest() for n in ['qwen_anchor_probe.py','qwen_anchor_workflow.py','sdk_runner.py','workflow.py']}}
 (root/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
 (root/'environment.txt').write_text(subprocess.check_output(['pip','freeze'],text=True),encoding='utf-8')
 output=io.BytesIO()
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
  for p in root.rglob('*'):
   if p.is_file():z.write(p,p.relative_to(root).as_posix())
  for p in Path('/tmp/anchor-sdk').rglob('*'):
   if p.is_file() and p.stat().st_size<100000:z.write(p,'sdk/'+p.name)
 return output.getvalue()
@app.local_entrypoint()
def main(source:str,identity:str,output:str,confirm_credits_only:bool=False,preflight_only:bool=False,full_reference_resolution:bool=False,prompt_file:str=''):
 if not confirm_credits_only:raise ValueError('Verify included credits and $0 cash spend cap first')
 check=preflight.remote();print(json.dumps(check),flush=True)
 if check['status']!='passed' or not check['model_files_present']:raise RuntimeError('CPU preflight failed; no GPU call')
 if preflight_only:
  Path(output).write_text(json.dumps(check,indent=2),encoding='utf-8');return
 dest=Path(output);dest.mkdir(parents=True,exist_ok=False)
 prompt=Path(prompt_file).read_text(encoding='utf-8') if prompt_file else PROMPT
 call=prepare.spawn(Path(source).read_bytes(),Path(identity).read_bytes(),prompt,full_reference_resolution)
 (dest/'modal-call.json').write_text(json.dumps({'call_id':call.object_id,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2),encoding='utf-8')
 print('Modal call receipt: '+call.object_id,flush=True)
 result=call.get()
 (dest/'evidence.zip').write_bytes(result)
 with zipfile.ZipFile(io.BytesIO(result)) as z:
  if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):raise ValueError('Unsafe archive')
  z.extractall(dest)
 record=json.loads((dest/'manifest.json').read_text(encoding='utf-8'))
 with (dest.parent/'anchor-ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
 print(record['status'],round(record['worker_elapsed_seconds'],2),flush=True)
 if record['failure']:raise RuntimeError('Failed reference test; inspect retained evidence before another call')
