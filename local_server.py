"""Optional local NVIDIA GPU backend, using the same inference code as Modal.

Run through Dockerfile.local. No Modal credentials or cloud calls are required.
"""
import asyncio
import hmac
import os
import time
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from media_pipeline import validate_payload, MAX_VIDEO_BYTES, MAX_IMAGE_BYTES

app = FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
jobs = {}
busy = False


@app.middleware("http")
async def authenticate(request,call_next):
    key = os.environ.get("OPENJUTSU_API_KEY","")
    if not key or not hmac.compare_digest(request.headers.get("authorization",""),"Bearer "+key):
        return JSONResponse({"error":"Unauthorized"},status_code=401)
    return await call_next(request)


@app.get("/status")
async def status():
    return {"configured":True,"features":{"objectSwap":True,"motionTransfer":True},
            "limits":{"maxVideoBytes":MAX_VIDEO_BYTES,"maxImageBytes":MAX_IMAGE_BYTES,
                      "maxFrames":33,"maxSide":480}}


async def render(job_id,data):
    global busy
    try:
        from service import generate
        result = await asyncio.to_thread(generate.local,data)
        jobs[job_id] = {"status":"succeeded","result":result}
    except Exception:
        jobs[job_id] = {"status":"failed","error":"Render failed. Check the local server log and GPU memory, then adjust the clip."}
        import traceback
        traceback.print_exc()
    finally:
        busy = False


@app.post("/jobs")
async def submit(request:Request):
    global busy
    size,chunks = 0,[]
    async for chunk in request.stream():
        size += len(chunk)
        if size >24*1024*1024:
            raise HTTPException(413,"Upload exceeds the prototype's limit")
        chunks.append(chunk)
    import json
    try:
        data = validate_payload(json.loads(b"".join(chunks)))
    except (ValueError,UnicodeError) as exc:
        raise HTTPException(400,str(exc)) from None
    if busy:
        raise HTTPException(429,"A local render is already running")
    busy = True
    job_id = uuid.uuid4().hex
    # In-memory results only: keep the four latest jobs and clear them on restart.
    if len(jobs)>=4:
        jobs.pop(next(iter(jobs)))
    jobs[job_id] = {"status":"running"}
    asyncio.create_task(render(job_id,data))
    return {"id":job_id}


@app.get("/jobs")
async def job(id:str):
    if id not in jobs:
        raise HTTPException(404,"Job not found or expired")
    return jobs[id]
