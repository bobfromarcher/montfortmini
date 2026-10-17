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

HERE = Path(__file__).parent
app = modal.App("openjutsu-studio")
api_secret = modal.Secret.from_name("openjutsu-site-api")
gpu_image = motion_base_image
for name in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
             "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
             "download_models.py","download_motion_models.py","media_pipeline.py"):
    gpu_image = gpu_image.add_local_file(HERE/name,"/root/"+name)
gpu_image = gpu_image.add_local_file(HERE/"media_pipeline.py","/opt/ComfyUI/custom_nodes/openjutsu_media.py")


@app.function(image=gpu_image,gpu="L40S",cpu=2,memory=32768,
              timeout=660,startup_timeout=180,max_containers=1,min_containers=0,
              scaledown_window=2,retries=0,single_use_containers=True)
def generate(data):
    from media_pipeline import prepare_media
    from workflow import build_graph
    from model_config import MODEL_REPO, MODEL_REVISION
    prepared = prepare_media(data)
    width,height,frames = prepared["width"],prepared["height"],prepared["frames"]
    mode = prepared["mode"]
    if mode=="motion-transfer":
        from motion_workflow import build_graph as motion_graph
        from motion_model_config import MODEL_REPO,MODEL_REVISION
        graph = motion_graph()
        graph["7"]["inputs"].update(reference_image=["6",2])
        graph["14"]["inputs"]["image"] = ["6",2]
    else:
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


cpu_image = (modal.Image.debian_slim(python_version="3.12")
             .pip_install("fastapi[standard]"))
for name in ("model_config.py","workflow.py","sdk_runner.py","modal_probe.py","motion_probe.py",
             "proof_inputs.py","motion_inputs.py","motion_workflow.py","motion_model_config.py",
             "download_models.py","download_motion_models.py","media_pipeline.py"):
    cpu_image = cpu_image.add_local_file(HERE/name,"/root/"+name)


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
                          "maxFrames":33,"maxSide":480}}

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
