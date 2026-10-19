"""Bounded, sequential, full-provenance evaluation on existing Modal images."""
import datetime,hashlib,io,json,os,time,zipfile
from pathlib import Path
import modal
import service

HERE=Path(__file__).parent
app=modal.App('montfortmini-validation')
image=(service.gpu_image
       .add_local_file(HERE/'service.py','/root/service.py')
       .add_local_file(HERE/'evaluation/baseline_media_pipeline.py','/root/baseline_media_pipeline.py')
       .add_local_file(HERE/'evaluation_inputs.py','/opt/ComfyUI/custom_nodes/montfortmini_evaluation.py'))

@app.function(image=image,cpu=2,memory=4096,timeout=240,max_containers=1,min_containers=0,scaledown_window=2,retries=0)
def audit_model_files():
    import subprocess
    from model_config import MODEL_FILES as vace_files
    from motion_model_config import MODEL_FILES as motion_files
    records=[];start=time.monotonic()
    for group,name in {**vace_files,**{('motion_'+k):v for k,v in motion_files.items()}}.items():
        folder=group.removeprefix('motion_')
        path=Path('/opt/ComfyUI/models')/folder/name
        digest=hashlib.sha256()
        with path.open('rb') as handle:
            while chunk:=handle.read(8*1024*1024):digest.update(chunk)
        records.append({'file':folder+'/'+name,'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
    return {'files':records,'comfy_commit':subprocess.check_output(['git','-C','/opt/ComfyUI','rev-parse','HEAD'],text=True).strip(),
            'audit_seconds':time.monotonic()-start,'environment':subprocess.check_output(['pip','freeze'],text=True)}

@app.function(image=image,gpu='L40S',cpu=2,memory=32768,timeout=660,startup_timeout=180,
              max_containers=1,min_containers=0,scaledown_window=2,retries=0,single_use_containers=True)
def evaluate(payload,case_info,profile='baseline',variant='baseline'):
    import subprocess,threading
    import media_pipeline
    start=time.monotonic()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if profile=='baseline':
        import baseline_media_pipeline
        media_pipeline.prepare_media=baseline_media_pipeline.prepare_media
    elif profile!='candidate': raise ValueError('Unknown profile')
    original=service.masked_replacement
    captured={}
    stop=threading.Event(); samples=[]
    def gpu_monitor():
        while not stop.is_set():
            try:
                line=subprocess.check_output(['nvidia-smi','--query-gpu=timestamp,name,utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],text=True,timeout=5).strip()
                samples.append(line)
            except Exception: pass
            stop.wait(1)
    monitor=threading.Thread(target=gpu_monitor,daemon=True);monitor.start()
    class Capture:
        @staticmethod
        def local(graph,info):
            root=Path('/tmp/openjutsu-fixture')
            settings=json.loads((root/'settings.json').read_text())
            settings['evaluation_variant']=variant
            (root/'settings.json').write_text(json.dumps(settings))
            import numpy as np
            from PIL import Image
            n=settings['frames']
            actual_source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(n)])
            actual_mask=np.stack([np.asarray(Image.open(root/'masks'/f'{i:04d}.png').convert('L'),dtype=np.float32)/255 for i in range(n)])
            actual_ref=np.asarray(Image.open(root/'reference.png').convert('RGB'),dtype=np.float32)/255
            if settings['mode']=='object-swap' and variant!='source-retained':actual_source=actual_source*(1-actual_mask[...,None])+.5*actual_mask[...,None]
            if variant=='frozen-motion':actual_source=np.repeat(actual_source[:1],n,axis=0)
            if variant=='neutral-reference':actual_ref=np.full_like(actual_ref,.5)
            np.savez_compressed(root/'conditioning.npz',source=actual_source,mask=actual_mask,reference=actual_ref)
            if variant in ('source-retained','frozen-motion','neutral-reference'):
                graph['6']['class_type']='OpenJutsuEvaluationInputs'
            elif variant not in ('baseline','repeat','reference-control','reference-alternate','reference-neutral','mask-coverage'):
                raise ValueError('Unknown ablation')
            archive=original.local(graph,info)
            captured['archive']=archive
            return archive
    service.masked_replacement=Capture()
    try:
        service.generate_legacy.local(payload)
    finally:
        stop.set();monitor.join(timeout=6)
        service.masked_replacement=original
    elapsed=time.monotonic()-start
    metadata={'case':case_info,'profile':profile,'variant':variant,'started_utc':started,
              'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'worker_elapsed_seconds':elapsed,'seed':payload.get('seed',42),
              'gpu_monitor_samples':len(samples),'input_video_sha256':hashlib.sha256(__import__('base64').b64decode(payload['video_b64'])).hexdigest(),
              'input_reference_sha256':hashlib.sha256(__import__('base64').b64decode(payload['reference_b64'])).hexdigest()}
    metadata['runtime_source_sha256']={name:hashlib.sha256((Path('/root')/name).read_bytes()).hexdigest() for name in
          ('service.py','workflow.py','motion_workflow.py','media_pipeline.py','baseline_media_pipeline.py','model_config.py','motion_model_config.py','evaluation_runner.py') if (Path('/root')/name).exists()}
    result=io.BytesIO(captured['archive'])
    with zipfile.ZipFile(result,'a',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('evaluation.json',json.dumps(metadata,indent=2))
        archive.writestr('gpu.csv','timestamp,gpu,utilization_percent,memory_MiB,power_W\n'+'\n'.join(samples))
        # Save the intervention's exact control, not just the original source.
        archive.writestr('intervention.json',json.dumps({'variant':variant,'erasure':payload['mode']=='object-swap' and variant!='source-retained',
                         'frozen_driving_frames':variant=='frozen-motion','neutral_reference':variant=='neutral-reference'}))
    return result.getvalue()

@app.local_entrypoint()
def main(dataset:str,output:str,case_ids:str='',profile:str='baseline',variant:str='baseline',seed:int=42,confirm_credits_only:bool=False,audit_models:bool=False):
    if not confirm_credits_only: raise ValueError('Verify included credits and $0 net spend first')
    import base64
    dataset_path=Path(dataset).resolve(); manifest=json.loads(dataset_path.read_text())
    ids=set(case_ids.split(',')) if case_ids else {c['id'] for c in manifest['cases'] if c['split']=='development'}
    if len(ids)>8: raise ValueError('At most eight cases per batch')
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
    if audit_models:
        record=audit_model_files.remote();(out.parent/'model-file-audit.json').write_text(json.dumps(record,indent=2));print('Saved remote model-file audit',flush=True);return
    ledger=out/'ledger.jsonl'
    records=[json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
    for case in manifest['cases']:
        if case['id'] not in ids: continue
        if len(records)>=24 or sum(r.get('worker_elapsed_seconds',0) for r in records)>=7200:
            raise RuntimeError('Evaluation budget reached')
        name=f"{case['id']}__{profile}__{variant}__s{seed}"
        destination=out/name
        if (destination/'evaluation.json').exists():
            print('SKIP existing '+name,flush=True);continue
        case=json.loads(json.dumps(case))
        data={k:case[k] for k in ('mode','prompt','frames','bbox','end_bbox')}
        data['seed']=seed
        if variant=='mask-coverage':
            if case['id']!='dev-real-object':raise ValueError('Mask coverage control is development-only')
            data['bbox']=data['end_bbox']=[.18,.20,.40,.50]
            case['bbox']=case['end_bbox']=data['bbox']
            case['notes'].append('Exploratory mask-coverage control: include the complete source sphere, whose left side is outside the originally registered rectangle. No model parameter changed.')
        for key,file_key in (('video_b64','video'),('reference_b64','reference')):
            path=dataset_path.parent/case[file_key]
            expected=case['sha256'][file_key]
            if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: raise ValueError('Input hash mismatch')
            data[key]=base64.b64encode(path.read_bytes()).decode()
        if variant.startswith('reference-'):
            # Reference-only contrast: same generic production prompt and seed.
            data['prompt']='';case['prompt']=''
            if variant!='reference-control':
                from PIL import Image
                import numpy as np
                ref=Image.open(io.BytesIO(base64.b64decode(data['reference_b64']))).convert('RGB')
                pixels=np.asarray(ref).copy()
                if variant=='reference-alternate':
                    region=(pixels[:,:,2]>pixels[:,:,0]*1.3)&(pixels[:,:,2]>pixels[:,:,1]*1.15)
                    pixels[region]=[40,165,75];case['annotations']['target_color']='green'
                else:pixels[:]=128
                buffer=io.BytesIO();Image.fromarray(pixels).save(buffer,format='PNG')
                data['reference_b64']=base64.b64encode(buffer.getvalue()).decode()
            case['notes'].append('Reference-only causal group: blank submitted prompt invokes the unchanged production default; only reference pixels differ between group members.')
        print('START '+name,flush=True); wall=time.monotonic()
        try:
            archive_bytes=evaluate.remote(data,{k:v for k,v in case.items() if k!='sha256'},profile,variant)
            destination.mkdir(exist_ok=True)
            (destination/'evidence.zip').write_bytes(archive_bytes)
            with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
                if any(not (destination/i.filename).resolve().is_relative_to(destination) for i in archive.infolist()): raise ValueError('Unsafe archive')
                archive.extractall(destination)
            record=json.loads((destination/'evaluation.json').read_text())
            record.update(run=name,status='succeeded',client_wall_seconds=time.monotonic()-wall,
                          archive_sha256=hashlib.sha256(archive_bytes).hexdigest())
            print('DONE '+name+' '+str(round(record['worker_elapsed_seconds'],2))+'s',flush=True)
        except Exception as exc:
            record={'run':name,'status':'failed','client_wall_seconds':time.monotonic()-wall,'error':str(exc)}
            print('FAILED '+name+' '+str(exc),flush=True)
        with ledger.open('a') as handle: handle.write(json.dumps(record)+'\n')
        records.append(record)
        if record['status']=='failed':raise RuntimeError('Stopped after recorded failure; inspect ledger before any manual retry')
