"""Private-key protected, on-demand app backend. GPU scales to zero."""
import base64
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import zipfile

import modal
from modal_probe import masked_replacement
from motion_probe import motion_base_image
from media_pipeline import validate_payload, MAX_VIDEO_BYTES, MAX_IMAGE_BYTES
import native_motion_backend

HERE = Path(__file__).parent
app = modal.App("openjutsu-studio")
app.include(native_motion_backend.app)
api_secret = modal.Secret.from_name("openjutsu-site-api")
gpu_image = motion_base_image
for name in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
             "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
             "download_models.py","download_motion_models.py","media_pipeline.py"):
    gpu_image = gpu_image.add_local_file(HERE/name,"/root/"+name)
gpu_image = gpu_image.add_local_file(HERE/"media_pipeline.py","/opt/ComfyUI/custom_nodes/openjutsu_media.py")
gpu_image = gpu_image.add_local_file(HERE/'legacy_local_inference.py', '/root/legacy_local_inference.py')
for name in native_motion_backend.SOURCE_NAMES:
    if name not in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
                    "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
                    "download_models.py","download_motion_models.py","media_pipeline.py"):
        gpu_image = gpu_image.add_local_file(HERE/name,"/root/"+name)
gpu_image = gpu_image.add_local_dir(HERE/'vendor/wan_animate', '/root/vendor/wan_animate')


@app.function(image=gpu_image,gpu="L40S",cpu=2,memory=32768,
              timeout=660,startup_timeout=180,max_containers=1,min_containers=0,
              scaledown_window=2,retries=0,single_use_containers=True)
def generate_object(data):
    from media_pipeline import prepare_media
    from workflow import build_graph
    from model_config import MODEL_REPO, MODEL_REVISION
    prepared = prepare_media(data)
    width,height,frames = prepared["width"],prepared["height"],prepared["frames"]
    mode = prepared["mode"]
    if mode != "object-swap":
        raise ValueError("Motion transfer must use the native motion backend")
    graph = build_graph(width=width,height=height,frames=frames)
    graph["6"] = {"class_type":"OpenJutsuMediaInputs","inputs":{}}
    graph["7"]["inputs"].update(width=width,height=height,length=frames)
    graph["9"]["inputs"]["seed"] = prepared["seed"]
    if prepared["prompt"]:
        graph["4"]["inputs"]["text"] = prepared["prompt"]
    elif mode=="object-swap":
        graph["4"]["inputs"]["text"] = "Replace the masked object with the object shown in the reference image. Natural motion, stable appearance, match the scene lighting."
    else:
        graph["4"]["inputs"]["text"] = "The character in the reference image performs the same movement as the source video. Stable character appearance, natural body motion, fixed framing."
    # Proof-specific negative words would bias arbitrary user edits.
    graph["5"]["inputs"]["text"] = "text, watermark, flicker, distorted shapes, extra limbs, duplicate subjects"
    archive_bytes = masked_replacement.local(graph,{
        "repo":MODEL_REPO,"revision":MODEL_REVISION,"mode":mode,
        "input_provenance":"user-selected video and reference image",
    })
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        return {
            "source_video_b64":base64.b64encode(archive.read("source.mp4")).decode(),
            "generated_video_b64":base64.b64encode(archive.read("generated.mp4")).decode(),
            "composite_video_b64":base64.b64encode(archive.read("composite.mp4")).decode(),
            "manifest":json.loads(archive.read("manifest.json")),
            "workflow":json.loads(archive.read("workflow-api.json")),
        }


@app.function(image=gpu_image,gpu='L40S',cpu=2,memory=32768,
              timeout=660,startup_timeout=180,max_containers=1,min_containers=0,
              scaledown_window=2,retries=0,single_use_containers=True)
def generate_legacy(data):
    """Keep historical evaluation capture hooks local to their old recipes."""
    import legacy_local_inference
    previous = legacy_local_inference.masked_replacement
    legacy_local_inference.masked_replacement = masked_replacement
    try:
        return legacy_local_inference.generate(data)
    finally:
        legacy_local_inference.masked_replacement = previous


cpu_image = (modal.Image.debian_slim(python_version="3.12")
             .pip_install("fastapi[standard]", "Pillow==13.0.0"))
for name in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
             "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
             "download_models.py","download_motion_models.py","media_pipeline.py"):
    cpu_image = cpu_image.add_local_file(HERE/name,"/root/"+name)
for name in native_motion_backend.SOURCE_NAMES:
    if name not in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
                    "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
                    "download_models.py","download_motion_models.py","media_pipeline.py"):
        cpu_image = cpu_image.add_local_file(HERE/name,"/root/"+name)
cpu_image = cpu_image.add_local_dir(HERE/'vendor/wan_animate', '/root/vendor/wan_animate')
cpu_image = cpu_image.add_local_file(HERE/'legacy_local_inference.py', '/root/legacy_local_inference.py')


@app.function(image=cpu_image, cpu=.25, memory=1024, timeout=1800,
              max_containers=1, min_containers=0, scaledown_window=2, retries=0,
              single_use_containers=True)
def generate(data, retain_evidence: bool = False):
    data = validate_payload(data)
    if data['mode'] == 'object-swap':
        return generate_object.remote(data)
    prepare_call = native_motion_backend.prepare.spawn(data)
    prepared = prepare_call.get()
    render_call = native_motion_backend.render.spawn(prepared['inputs'], prepared['graph'])
    bundle = render_call.get()
    stream = io.BytesIO(bundle)
    with zipfile.ZipFile(stream, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('service-job.json', json.dumps({'prepare_call_id': prepare_call.object_id,
            'render_call_id': render_call.object_id, 'service_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, indent=2))
    bundle = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        record = json.loads(archive.read('candidate.json'))
        if record['status'] != 'succeeded':
            if retain_evidence:
                return {'evidence_zip': bundle, 'technical_failure': record['failure']}
            raise RuntimeError('Native motion worker did not complete; no automatic retry')
        result = {
            'source_video_b64': base64.b64encode(archive.read('source.mp4')).decode(),
            'generated_video_b64': base64.b64encode(archive.read('generated.mp4')).decode(),
            'composite_video_b64': base64.b64encode(archive.read('composite.mp4')).decode(),
            'manifest': json.loads(archive.read('manifest.json')),
            'workflow': json.loads(archive.read('workflow-api.json')),
        }
        if retain_evidence:
            result['evidence_zip'] = bundle
        return result


@app.local_entrypoint()
def verify_native(directory: str, confirm_credits_only: bool = False):
    """One bounded call through the exact app orchestrator; no deployment."""
    root = Path(directory)
    frozen = json.loads((root/'freeze.json').read_text(encoding='utf-8'))
    if not confirm_credits_only or frozen['budget']['cash_cap'] != 0 or frozen['budget']['included_cap'] != 1:
        raise ValueError('Credits-only authorization and frozen $1 budget required')
    ledger = root/'gpu-ledger.json'
    if ledger.exists():
        raise ValueError('An integration reservation already exists; no retry')
    for name, digest in frozen['source_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen app source changed: '+name)
    for name, digest in frozen['artifact_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen integration input changed: '+name)
    data = validate_payload(json.loads((root/'request.json').read_text(encoding='utf-8')))
    if data['mode'] != 'motion-transfer':
        raise ValueError('Integration fixture must be motion transfer')
    row = {'status':'reserved','max_gpu_calls':1,'max_gpu_seconds':900,'max_controls_seconds':900}
    ledger.write_text(json.dumps([row],indent=2))
    try:
        call = generate.spawn(data, retain_evidence=True)
        row.update(status='dispatched', orchestrator_call_id=call.object_id)
        ledger.write_text(json.dumps([row],indent=2))
        print('App call receipt: '+call.object_id,flush=True)
        result = call.get()
        bundle = result.pop('evidence_zip')
        dest = root/'result'; dest.mkdir(exist_ok=False)
        (dest/'evidence.zip').write_bytes(bundle)
        with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
            if any(not (dest/item.filename).resolve().is_relative_to(dest.resolve()) for item in archive.infolist()):
                raise ValueError('Unsafe evidence archive')
            archive.extractall(dest)
        if result.get('technical_failure'):
            raise RuntimeError('Native worker failed; full evidence retained; no retry')
        for key,name in [('source_video_b64','app-source.mp4'),('generated_video_b64','app-generated.mp4'),('composite_video_b64','app-composite.mp4')]:
            (dest/name).write_bytes(base64.b64decode(result.pop(key)))
        (dest/'app-response.json').write_text(json.dumps(result,indent=2))
        row.update(status='succeeded', **json.loads((dest/'service-job.json').read_text()))
        print('App integration completed',flush=True)
    except Exception as exc:
        row.update(status='failed',exception_type=type(exc).__name__)
        raise
    finally:
        ledger.write_text(json.dumps([row],indent=2))


@app.function(image=cpu_image,cpu=.25,memory=512,timeout=40,
              max_containers=2,min_containers=0,scaledown_window=2,secrets=[api_secret])
@modal.asgi_app()
def api():
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    service = FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    key = os.environ["OPENJUTSU_API_KEY"]

    @service.middleware("http")
    async def authenticate(request,call_next):
        supplied = request.headers.get("authorization","")
        if not hmac.compare_digest(supplied,"Bearer "+key):
            return JSONResponse({"error":"Unauthorized"},status_code=401)
        return await call_next(request)

    @service.get("/status")
    async def status():
        return {"configured":True,"features":{"objectSwap":True,"motionTransfer":True},
                "limits":{"maxVideoBytes":MAX_VIDEO_BYTES,"maxImageBytes":MAX_IMAGE_BYTES,
                          "maxFrames":33,"maxSide":560}}

    @service.post("/jobs")
    async def submit(request:Request):
        size = 0
        chunks = []
        async for chunk in request.stream():
            size += len(chunk)
            if size > 24*1024*1024:
                raise HTTPException(413,"Upload exceeds the prototype's limit")
            chunks.append(chunk)
        try:
            data = validate_payload(json.loads(b"".join(chunks)))
        except (ValueError,UnicodeError) as exc:
            raise HTTPException(400,str(exc)) from None
        call = await generate.spawn.aio(data)
        call_id = call.object_id
        signature = hmac.new(key.encode(),call_id.encode(),hashlib.sha256).hexdigest()
        return {"id":call_id+"."+signature}

    @service.get("/jobs")
    async def job(id:str):
        try:
            call_id,signature = id.rsplit(".",1)
        except ValueError:
            raise HTTPException(400,"Invalid job identifier") from None
        expected = hmac.new(key.encode(),call_id.encode(),hashlib.sha256).hexdigest()
        if not call_id.startswith("fc-") or not hmac.compare_digest(signature,expected):
            raise HTTPException(404,"Job not found")
        try:
            result = await modal.FunctionCall.from_id(call_id).get.aio(timeout=0)
        except TimeoutError:
            return {"status":"running"}
        except Exception:
            return {"status":"failed","error":"The render could not complete. Try a shorter clip or a different reference; no automatic retry was started."}
        return {"status":"succeeded","result":result}
    return service
