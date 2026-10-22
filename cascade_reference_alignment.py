"""Experimental composition correction followed by identity refinement.

Each native image-edit stage is archived separately. No generated video frame
is repaired or blended after motion inference.
"""
import hashlib,io,json,zipfile
from pathlib import Path
from reference_alignment import run_reference_alignment as klein_edit
from qwen_reference_alignment import run_reference_alignment as qwen_edit
from anchor_workflow import FILES as KLEIN_FILES
from qwen_anchor_workflow import FILES as QWEN_FILES
FILES=KLEIN_FILES+QWEN_FILES

def run_reference_alignment(source,identity):
 stages=[];archives=[];final=None;failure=None
 for name,editor in [('klein',klein_edit),('qwen',qwen_edit)]:
  data=editor(source if final is None else final,identity,output_directory='/tmp/reference-'+name)
  archives.append((name,data))
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   manifest=json.loads(z.read('manifest.json'));stages.append({'stage':name,**manifest})
   if manifest['status']!='succeeded':failure={'stage':name,'detail':manifest.get('failure')};break
   final=z.read('anchor.png')
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in archives:
   with zipfile.ZipFile(io.BytesIO(data)) as a:
    for f in a.infolist():
     if not f.is_dir():z.writestr(name+'/'+f.filename,a.read(f))
  if final is not None and failure is None:z.writestr('anchor.png',final)
  z.writestr('manifest.json',json.dumps({'status':'failed' if failure else 'succeeded','failure':failure,'stages':stages,'worker_elapsed_seconds':sum(s['worker_elapsed_seconds'] for s in stages),'original_source_sha256':hashlib.sha256(source).hexdigest(),'original_identity_sha256':hashlib.sha256(identity).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'limitations':['Reference preparation may redraw source pixels; no outside-region preservation claim.','Reference quality and video quality must be evaluated separately.']},indent=2))
 return out.getvalue()
