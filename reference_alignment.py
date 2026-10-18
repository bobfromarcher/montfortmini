"""Native open-model pose-matched reference preparation; no external API calls.

The source frame supplies pose/framing; the uploaded character supplies appearance.
Image preparation is recorded separately from the subsequent video generation.
"""
import datetime,hashlib,io,json,math,time,zipfile
from pathlib import Path
from anchor_workflow import build_graph,FILES
DEFAULT_PROMPT=("Replace the person in image 1 with the character from image 2. "
 "Preserve the character's face shape, hair, clothing, colors and accessories from image 2. "
 "Keep the body position, head direction, hand positions, camera framing and perspective from image 1. "
 "Preserve the background, furniture, held objects and scene lighting from image 1. "
 "One character with natural anatomy, rendered in the visual style of image 2.")
def reference_prompt(character_description=''):
 prompt=DEFAULT_PROMPT
 if character_description.strip():prompt+='\nTarget character description from the user: '+character_description.strip()
 return prompt+'\nKeep both hands in the source positions. Do not add unrelated objects or props.'
def source_canvas(width,height):
 if width<=0 or height<=0 or not .25<=width/height<=4:
  raise ValueError('Motion reference preparation supports source aspect ratios from 1:4 to 4:1')
 scale=math.sqrt((768*1360)/(width*height))
 return (max(128,round(width*scale/16)*16),max(128,round(height*scale/16)*16))

def identity_canvas(width,height):
 if width<=0 or height<=0:raise ValueError('Empty character reference')
 scale=512/max(width,height)
 return (max(16,round(width*scale/16)*16),max(16,round(height*scale/16)*16))

def run_reference_alignment(source,identity,prompt=DEFAULT_PROMPT,full_reference_resolution=False,output_directory='/tmp/anchor-evidence'):
 import subprocess,threading,psutil
 from urllib.request import urlopen
 from PIL import Image,ImageOps
 from workflow import validate_graph
 from sdk_runner import run_with_sdk
 start=time.monotonic();started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat();root=Path(output_directory);root.mkdir(exist_ok=True)
 target=Path('/opt/ComfyUI/input');target.mkdir(exist_ok=True)
 with Image.open(io.BytesIO(source)) as original:canvas=source_canvas(*ImageOps.exif_transpose(original).size)
 for name,data,size in [('source',source,canvas),('identity',identity,None)]:
  (root/(name+'-original.png')).write_bytes(data)
  with Image.open(io.BytesIO(data)) as im:
   im=ImageOps.exif_transpose(im).convert('RGB')
   if size:im=im.resize(size,Image.Resampling.LANCZOS)
   else:
    im=im.resize(identity_canvas(*im.size),Image.Resampling.LANCZOS)
    if full_reference_resolution:im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
   im.save(target/('recovery-'+name+'.png'));im.save(root/(name+'-conditioning.png'))
 graph=build_graph(prompt,width=canvas[0],height=canvas[1]);(root/'workflow-api.json').write_text(json.dumps(graph,indent=2),encoding='utf-8')
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
 metadata={'status':'failed' if failure else 'succeeded','failure':failure,'worker_elapsed_seconds':time.monotonic()-start,'sdk_receipt':receipt,'models':FILES,'prompt':prompt,'seed':42,'started_utc':started_utc,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_reference_resolution':full_reference_resolution,'source_sha256':hashlib.sha256(source).hexdigest(),'identity_sha256':hashlib.sha256(identity).hexdigest(),'software_sha256':{n:hashlib.sha256((Path('/root')/n).read_bytes()).hexdigest() for n in ['reference_alignment.py','anchor_workflow.py','sdk_runner.py','workflow.py']}}
 (root/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
 (root/'environment.txt').write_text(subprocess.check_output(['pip','freeze'],text=True),encoding='utf-8')
 output=io.BytesIO()
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
  for p in root.rglob('*'):
   if p.is_file():z.write(p,p.relative_to(root).as_posix())
  for p in Path('/tmp/anchor-sdk').rglob('*'):
   if p.is_file() and p.stat().st_size<100000:z.write(p,'sdk/'+p.name)
 return output.getvalue()
