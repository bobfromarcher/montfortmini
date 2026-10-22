"""Bounded quality experiments; candidate fitting was evaluated, not shipped.

Historical profile 'production' means default-prompt cover experiment, not the
released pipeline. Frozen baseline/pre-cover/candidate modules preserve recipes.
"""
import base64,datetime,hashlib,io,json,threading,time,zipfile
from pathlib import Path
import modal
import service
HERE=Path(__file__).parent
app=modal.App('montfortmini-fidelity')
image=(service.gpu_image.add_local_file(HERE/'service.py','/root/service.py')
       .add_local_file(HERE/'evaluation/fidelity_baseline_media_pipeline.py','/root/fidelity_baseline_media_pipeline.py')
       .add_local_file(HERE/'evaluation/fidelity_precover_media_pipeline.py','/root/fidelity_precover_media_pipeline.py')
       .add_local_file(HERE/'evaluation/fidelity_candidate_media_pipeline.py','/root/fidelity_candidate_media_pipeline.py')
       .add_local_file(HERE/'evaluation/fidelity_baseline_motion_workflow.py','/root/fidelity_baseline_motion_workflow.py'))
PROFILES=('sheet','crop','describe','separate','native','reference','window','cover','fullbody','production','baseline','candidate')

@app.function(image=image,cpu=2,memory=2048,timeout=240,max_containers=1,min_containers=0,scaledown_window=2,retries=0)
def audit_vae_equivalence():
    import struct
    from huggingface_hub import hf_hub_download
    start=time.monotonic()
    alternate=Path(hf_hub_download('Comfy-Org/Wan-Animate-2','vae/Wan2_1_VAE_bf16.safetensors',revision='e7181fe1896b7f2ce34120d1a3663413548240d7'))
    result={}
    for name,path in [('shared',Path('/opt/ComfyUI/models/vae/wan_2.1_vae.safetensors')),('official_animate',alternate)]:
        digest=hashlib.sha256()
        with path.open('rb') as f:
            header_size=struct.unpack('<Q',f.read(8))[0];header=json.loads(f.read(header_size))
            while chunk:=f.read(8*1024*1024):digest.update(chunk)
        result[name]={'file_bytes':path.stat().st_size,'header_bytes':header_size,'payload_sha256':digest.hexdigest(),
                      'tensor_headers':{k:v for k,v in header.items() if k!='__metadata__'}}
    result['tensor_bytes_equal']=result['shared']['payload_sha256']==result['official_animate']['payload_sha256']
    result['tensor_headers_equal']=result['shared']['tensor_headers']==result['official_animate']['tensor_headers']
    result['cpu_audit_seconds']=time.monotonic()-start
    return result

@app.function(image=image,gpu='L40S',cpu=2,memory=32768,timeout=660,startup_timeout=180,
              max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def render(payload,case,profile):
    import subprocess,psutil,numpy as np
    from PIL import Image
    import media_pipeline,motion_workflow,fidelity_baseline_media_pipeline,fidelity_baseline_motion_workflow,fidelity_precover_media_pipeline,fidelity_candidate_media_pipeline
    index=PROFILES.index(profile) if profile in PROFILES[:7] else (4 if profile in ('cover','fullbody') else 0)
    start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    saved_prepare=media_pipeline.prepare_media;saved_graph=motion_workflow.build_graph;saved_runner=service.masked_replacement
    motion_workflow.build_graph=fidelity_baseline_motion_workflow.build_graph
    media_pipeline.prepare_media=(lambda data:fidelity_precover_media_pipeline.prepare_media(data,max_side=864,target_short_side=480)) if index>=4 else (fidelity_candidate_media_pipeline.prepare_media if profile=='candidate' else fidelity_baseline_media_pipeline.prepare_media)
    samples=[];stop=threading.Event();process=psutil.Process()
    def monitor():
        while not stop.is_set():
            try:
                line=subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,name,utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],text=True,timeout=5).strip()
                tree=[process]+process.children(recursive=True)
                rss=sum(p.memory_info().rss for p in tree if p.is_running())/1024**2
                samples.append(line+','+str(round(rss,2)))
            except Exception:pass
            stop.wait(1)
    thread=threading.Thread(target=monitor,daemon=True);thread.start();captured={}
    class Capture:
        @staticmethod
        def local(graph,info):
            root=Path('/tmp/openjutsu-fixture')
            if profile in ('cover','fullbody','production'):
                settings=json.loads((root/'settings.json').read_text(encoding='utf-8'))
                from PIL import ImageOps
                with Image.open(root/'uploaded-reference') as ref:
                    ImageOps.fit(ImageOps.exif_transpose(ref).convert('RGB'),(settings['width'],settings['height']),method=Image.Resampling.BICUBIC).save(root/'reference.png')
            if index>=2 and profile!='production':graph['4']['inputs']['text']=case['prompt']
            if index>=3 and profile!='production':
                graph['17']={'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':case.get('pose_prompt','')}}
                graph['7']['inputs']['positive_pose']=['17',0]
            if index>=5:graph['7']['inputs']['reference_image_strength']=1.3
            if index>=6:graph['7']['inputs']['pose_end_percent']=.7
            root=Path('/tmp/openjutsu-fixture');settings=json.loads((root/'settings.json').read_text(encoding='utf-8'));n=settings['frames']
            source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(n)])
            mask=np.stack([np.asarray(Image.open(root/'masks'/f'{i:04d}.png').convert('L'),dtype=np.float32)/255 for i in range(n)])
            reference=np.asarray(Image.open(root/'reference.png').convert('RGB'),dtype=np.float32)/255
            if settings['mode']=='object-swap':source=media_pipeline.erase_target(source,mask)
            np.savez_compressed(root/'conditioning.npz',source=source,mask=mask,reference=reference)
            captured['graph']=graph;captured['archive']=saved_runner.local(graph,info)
            return captured['archive']
    service.masked_replacement=Capture()
    failure=None
    try:service.generate_legacy.local(payload)
    except Exception as exc:
        failure={'type':type(exc).__name__,'message':str(exc)}
        failed=io.BytesIO()
        with zipfile.ZipFile(failed,'w',zipfile.ZIP_DEFLATED) as z:
            for folder,prefix in [(Path('/tmp/openjutsu-fixture'),'inputs/'),(Path('/tmp/openjutsu-sdk-output'),'sdk/')]:
                if folder.exists():
                    for file in folder.rglob('*'):
                        if file.is_file():z.write(file,prefix+file.relative_to(folder).as_posix())
            if Path('/tmp/comfy.log').exists():z.write('/tmp/comfy.log','comfy.log')
            z.writestr('workflow-api.json',json.dumps(captured.get('graph',{}),indent=2))
            z.writestr('failure.json',json.dumps(failure,indent=2))
        captured['archive']=failed.getvalue()
    finally:
        stop.set();thread.join(timeout=6);media_pipeline.prepare_media=saved_prepare
        motion_workflow.build_graph=saved_graph;service.masked_replacement=saved_runner
    metadata={'case':case,'profile':profile,'seed':payload['seed'],'started_utc':started,'status':'failed' if failure else 'succeeded','failure':failure,
       'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_elapsed_seconds':time.monotonic()-start,
       'input_video_sha256':hashlib.sha256(base64.b64decode(payload['video_b64'])).hexdigest(),
       'input_reference_sha256':hashlib.sha256(base64.b64decode(payload['reference_b64'])).hexdigest(),
       'source_sha256':{n:hashlib.sha256((Path('/root')/n).read_bytes()).hexdigest() for n in ('media_pipeline.py','motion_workflow.py','service.py','sdk_runner.py','fidelity_baseline_media_pipeline.py','fidelity_baseline_motion_workflow.py','fidelity_precover_media_pipeline.py','fidelity_candidate_media_pipeline.py','fidelity_runner.py','model_config.py','motion_model_config.py') if (Path('/root')/n).exists()},
       'client_runner_sha256':case.get('_client_runner_sha256'),
       'limits':['Agent visual assessment, not an independent professional score.','Process-tree RSS sums may count shared pages twice; GPU peaks are sampled at 1 Hz.']}
    result=io.BytesIO(captured['archive'])
    with zipfile.ZipFile(result,'a',zipfile.ZIP_DEFLATED) as z:
        z.writestr('fidelity.json',json.dumps(metadata,indent=2));z.writestr('gpu.csv','timestamp,gpu,utilization_percent,memory_MiB,power_W,process_tree_rss_MiB\n'+'\n'.join(samples))
    return result.getvalue()

@app.local_entrypoint()
def main(cases:str,output:str,case:str='portrait',profile:str='sheet',seed:int=42,confirm_credits_only:bool=False,audit_vae:bool=False):
    if not confirm_credits_only:raise ValueError('Verify included credits and $0 net spend cap first')
    if profile not in PROFILES:raise ValueError('Unknown profile')
    cases_file=Path(cases).resolve();spec=json.loads(cases_file.read_text(encoding='utf-8'))[case];out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
    if audit_vae:
        record=audit_vae_equivalence.remote();(out.parent/'vae-equivalence.json').write_text(json.dumps(record,indent=2), encoding='utf-8');print('Saved VAE tensor-payload audit',flush=True);return
    ledger=out/'ledger.jsonl';records=[json.loads(s) for s in ledger.read_text(encoding='utf-8').splitlines()] if ledger.exists() else []
    if len(records)>=16 or sum(r.get('worker_elapsed_seconds',r.get('client_wall_seconds',0)) for r in records)>=6000:raise RuntimeError('Phase budget reached')
    name=f'{case}__{profile}__s{seed}';dest=out/name
    if (dest/'fidelity.json').exists():print('SKIP '+name);return
    ref=spec['reference'] if profile=='sheet' else spec.get('crop_reference',spec['reference'])
    if profile=='fullbody':ref=spec.get('fullbody_reference',ref)
    for key,path in [('video',spec['video']),('reference',ref)]:
        if key in spec.get('sha256',{}) and hashlib.sha256((cases_file.parent/path).read_bytes()).hexdigest()!=spec['sha256'][key]:raise ValueError('Frozen input hash mismatch: '+key)
    payload={'mode':spec.get('mode','motion-transfer'),'frames':spec.get('frames',17),'seed':seed,'prompt':spec.get('prompt','') if profile in ('candidate','baseline') else '',
      'bbox':spec.get('bbox',[0,0,1,1]),'end_bbox':spec.get('end_bbox',spec.get('bbox',[0,0,1,1])),
      'video_b64':base64.b64encode((cases_file.parent/spec['video']).read_bytes()).decode(),
      'reference_b64':base64.b64encode((cases_file.parent/ref).read_bytes()).decode()}
    print('START '+name,flush=True);start=time.monotonic()
    try:
        result=render.remote(payload,{**spec,'id':case,'_client_runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},profile);dest.mkdir(exist_ok=True);(dest/'evidence.zip').write_bytes(result)
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            if any(not (dest/i.filename).resolve().is_relative_to(dest) for i in z.infolist()):raise ValueError('Unsafe archive')
            z.extractall(dest)
        record=json.loads((dest/'fidelity.json').read_text(encoding='utf-8'));record.update(run=name,client_wall_seconds=time.monotonic()-start,archive_sha256=hashlib.sha256(result).hexdigest())
        print(('DONE ' if record['status']=='succeeded' else 'FAILED ')+name+' '+str(round(record['worker_elapsed_seconds'],2))+'s',flush=True)
    except Exception as exc:record={'run':name,'status':'failed','error':str(exc),'client_wall_seconds':time.monotonic()-start}
    with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    if record['status']!='succeeded':raise RuntimeError('Recorded failure; stop and inspect before any retry')
