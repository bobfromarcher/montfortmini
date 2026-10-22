"""Frozen, private two-stage motion correction candidate. Not production yet."""
import base64,datetime,hashlib,io,json,threading,time,zipfile
from pathlib import Path
import modal
import service
HERE=Path(__file__).parent
app=modal.App('montfortmini-alignment-candidate')
image=(service.motion_base_image
 .add_local_file(HERE/'anchor_workflow.py','/root/anchor_workflow.py',copy=True)
 .run_commands('timeout 900 python /root/anchor_workflow.py'))
for name in ('model_config.py','workflow.py','sdk_runner.py','modal_probe.py','motion_probe.py','proof_inputs.py',
 'motion_inputs.py','motion_workflow.py','motion_model_config.py','download_models.py','download_motion_models.py',
 'media_pipeline.py','service.py','reference_alignment.py'):
 image=image.add_local_file(HERE/name,'/root/'+name)
image=(image.add_local_file(HERE/'media_pipeline.py','/opt/ComfyUI/custom_nodes/openjutsu_media.py')
 .add_local_file(HERE/'evaluation/fidelity_precover_media_pipeline.py','/root/fidelity_precover_media_pipeline.py'))
@app.function(image=image,cpu=1,memory=512,timeout=60,max_containers=1,min_containers=0,scaledown_window=2,retries=0)
def preflight():
 from reference_alignment import run_reference_alignment
 from anchor_workflow import FILES
 return {'imports_passed':callable(run_reference_alignment),'models_present':all((Path('/opt/ComfyUI/models')/f[3]).is_file() for f in FILES)}
@app.function(image=image,gpu='L40S',cpu=2,memory=65536,timeout=660,startup_timeout=180,
 max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def render(payload):
 import subprocess,numpy as np
 from PIL import Image,ImageOps
 import media_pipeline,motion_workflow,fidelity_precover_media_pipeline
 from reference_alignment import run_reference_alignment,DEFAULT_PROMPT
 start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat();samples=[];stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],text=True,timeout=5).strip()
    current=Path('/sys/fs/cgroup/memory.current');peak=Path('/sys/fs/cgroup/memory.peak')
    samples.append(gpu+','+(current.read_text().strip() if current.exists() else '')+','+(peak.read_text().strip() if peak.exists() else ''))
   except Exception:pass
   stop.wait(1)
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 saved_prepare=media_pipeline.prepare_media;saved_runner=service.masked_replacement
 def prepare(data):
  if data['mode']=='motion-transfer':return fidelity_precover_media_pipeline.prepare_media(data,max_side=864,target_short_side=480)
  return saved_prepare(data)
 media_pipeline.prepare_media=prepare;captured={};failure=None
 class Capture:
  @staticmethod
  def local(graph,info):
   root=Path('/tmp/openjutsu-fixture');cfg=json.loads((root/'settings.json').read_text(encoding='utf-8'))
   if cfg['mode']=='motion-transfer':
    original=root/'anchor-original-source.png'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(root/'uploaded-video'),'-frames:v','1',str(original)],check=True,capture_output=True,timeout=30)
    anchor=run_reference_alignment(original.read_bytes(),(root/'uploaded-reference').read_bytes())
    captured['anchor_archive']=anchor
    with zipfile.ZipFile(io.BytesIO(anchor)) as z:
     check=json.loads(z.read('manifest.json'))
     if check['status']!='succeeded':raise RuntimeError('Reference preparation failed; no motion job submitted')
     with Image.open(io.BytesIO(z.read('anchor.png'))) as im:ImageOps.fit(im.convert('RGB'),(cfg['width'],cfg['height']),method=Image.Resampling.BICUBIC).save(root/'reference.png')
    graph['17']={'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':'A person performs the movements shown in the driving video.'}}
    graph['7']['inputs']['positive_pose']=['17',0]
   n=cfg['frames'];source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(n)])
   mask=np.stack([np.asarray(Image.open(root/'masks'/f'{i:04d}.png').convert('L'),dtype=np.float32)/255 for i in range(n)])
   ref=np.asarray(Image.open(root/'reference.png').convert('RGB'),dtype=np.float32)/255
   if cfg['mode']=='object-swap':source=media_pipeline.erase_target(source,mask)
   np.savez_compressed(root/'conditioning.npz',source=source,mask=mask,reference=ref)
   captured['archive']=saved_runner.local(graph,info);return captured['archive']
 service.masked_replacement=Capture()
 try:service.generate_legacy.local(payload)
 except Exception as e:failure={'type':type(e).__name__,'message':str(e)}
 finally:
  stop.set();thread.join(timeout=6);media_pipeline.prepare_media=saved_prepare;service.masked_replacement=saved_runner
 result=io.BytesIO(captured.get('archive',b''))
 with zipfile.ZipFile(result,'a',zipfile.ZIP_DEFLATED) as z:
  if 'anchor_archive' in captured:
   with zipfile.ZipFile(io.BytesIO(captured['anchor_archive'])) as a:
    for i in a.infolist():
     if not i.is_dir():z.writestr('reference-preparation/'+i.filename,a.read(i))
  z.writestr('candidate.json',json.dumps({'status':'failed' if failure else 'succeeded','failure':failure,'started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_elapsed_seconds':time.monotonic()-start,'allocated_memory_MiB':65536,'source_sha256':{name:hashlib.sha256((Path('/root')/name).read_bytes()).hexdigest() for name in ['alignment_candidate.py','reference_alignment.py','anchor_workflow.py','service.py','media_pipeline.py','fidelity_precover_media_pipeline.py','motion_workflow.py','sdk_runner.py']}},indent=2))
  z.writestr('candidate-gpu.csv','timestamp,utilization_percent,memory_MiB,power_W,cgroup_memory_current_bytes,cgroup_memory_peak_bytes\n'+'\n'.join(samples))
 return result.getvalue()
@app.local_entrypoint()
def main(cases:str,case:str,output:str,confirm_credits_only:bool=False,frames:int=33,preflight_only:bool=False):
 if not confirm_credits_only:raise ValueError('Verify included credits and $0 cash cap')
 check=preflight.remote();print('CPU preflight '+json.dumps(check),flush=True)
 if not all(check.values()):raise RuntimeError('Candidate CPU preflight failed; no GPU call')
 if preflight_only:
  Path(output).write_text(json.dumps(check,indent=2),encoding='utf-8');return
 path=Path(cases).resolve();spec=json.loads(path.read_text(encoding='utf-8'))[case];dest=Path(output);dest.mkdir(parents=True,exist_ok=False)
 payload={'mode':spec.get('mode','motion-transfer'),'frames':frames,'seed':42,'prompt':spec.get('prompt',''),'bbox':spec.get('bbox',[0,0,1,1]),'end_bbox':spec.get('end_bbox',spec.get('bbox',[0,0,1,1])),
 'video_b64':base64.b64encode((path.parent/spec['video']).read_bytes()).decode(),'reference_b64':base64.b64encode((path.parent/spec['reference']).read_bytes()).decode()}
 call=render.spawn(payload);(dest/'modal-call.json').write_text(json.dumps({'call_id':call.object_id,'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2),encoding='utf-8');print('Modal call receipt: '+call.object_id,flush=True)
 data=call.get();(dest/'evidence.zip').write_bytes(data)
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  if any(not (dest/i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):raise ValueError('Unsafe archive')
  z.extractall(dest)
 record=json.loads((dest/'candidate.json').read_text(encoding='utf-8'));print(record['status'],round(record['worker_elapsed_seconds'],2),flush=True)
 if record['failure']:raise RuntimeError('Candidate failed; inspect evidence before another call')
