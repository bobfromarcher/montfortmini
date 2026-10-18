"""Bounded, on-demand feasibility job. Importing this file does not run it."""
import io
import json
from pathlib import Path
import zipfile

import modal
from workflow import COMFY_COMMIT, MODEL_REPO, MODEL_REVISION, MODEL_FILES, build_graph, validate_graph

HERE = Path(__file__).parent
REMOTE = "/opt/ComfyUI"
app = modal.App("openjutsu-feasibility")


base_image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg", "libgl1", "libglib2.0-0")
    .run_commands(
        f"git init {REMOTE}",
        f"git -C {REMOTE} remote add origin https://github.com/Comfy-Org/ComfyUI.git",
        f"git -C {REMOTE} fetch --depth 1 origin {COMFY_COMMIT}",
        f"git -C {REMOTE} checkout --detach FETCH_HEAD",
    )
    .uv_pip_install("torch==2.9.1", "torchvision==0.24.1", "torchaudio==2.9.1",
                    index_url="https://download.pytorch.org/whl/cu128")
    .run_commands(f"pip install -r {REMOTE}/requirements.txt huggingface_hub==0.36.0")
    .add_local_file(HERE / "model_config.py", "/root/model_config.py", copy=True)
    .add_local_file(HERE / "download_models.py", "/root/download_models.py", copy=True)
    .run_commands("timeout 900 python /root/download_models.py")
    .uv_pip_install("comfy-api-proxy==0.1.6", "comfy-sdk==0.5.0")
    .env({"PYTHONPATH":"/root", "HF_HUB_DISABLE_TELEMETRY":"1"})
)
image = (base_image
    .add_local_file(HERE / "workflow.py", "/root/workflow.py")
    .add_local_file(HERE / "sdk_runner.py", "/root/sdk_runner.py")
    .add_local_file(HERE / "proof_inputs.py", f"{REMOTE}/custom_nodes/openjutsu_proof.py")
)


def request_json(path, data=None):
    from urllib.request import Request, urlopen
    req = Request("http://127.0.0.1:8188" + path,
                  data=None if data is None else json.dumps(data).encode(),
                  headers={"Content-Type":"application/json"})
    with urlopen(req, timeout=10) as response:
        return json.load(response)


@app.function(image=image, gpu="L40S", cpu=2, memory=16384,
              timeout=600, startup_timeout=180, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0)
def masked_replacement(graph_override=None, model_info=None):
    import subprocess
    import time
    from PIL import Image, ImageDraw

    start = time.monotonic()
    import shutil
    for old_output in ("/tmp/openjutsu-result","/tmp/openjutsu-sdk-output"):
        shutil.rmtree(old_output,ignore_errors=True)
    graph = graph_override or build_graph()
    model_info = model_info or {"repo":MODEL_REPO,"revision":MODEL_REVISION,"mode":"object-swap"}
    frame_count = graph["7"]["inputs"]["length"]
    width = graph["7"]["inputs"]["width"]
    height = graph["7"]["inputs"]["height"]
    log_path = Path("/tmp/comfy.log")
    log = log_path.open("w")
    proc = subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188",
                             "--disable-auto-launch", "--preview-method", "none"], cwd=REMOTE,
                            stdout=log, stderr=subprocess.STDOUT)
    proxy = None
    try:
        deadline = start + 560
        while True:
            if proc.poll() is not None:
                raise RuntimeError("Comfy startup failed:\n" + log_path.read_text()[-7000:])
            try:
                schema = request_json("/object_info")
                break
            except (OSError, ValueError):
                if time.monotonic() - start > 90:
                    raise RuntimeError("Comfy startup timed out:\n"+log_path.read_text()[-7000:])
                time.sleep(1)
        validate_graph(graph, schema)
        from urllib.request import urlopen
        from sdk_runner import run_with_sdk
        proxy = subprocess.Popen(["comfy-api-proxy","--comfyui","http://127.0.0.1:8188","--port","8189"],
                                 stdout=log, stderr=subprocess.STDOUT)
        proxy_deadline = time.monotonic() + 30
        while True:
            if proxy.poll() is not None:
                raise RuntimeError("Comfy SDK proxy exited:\n" + log_path.read_text()[-4000:])
            try:
                with urlopen("http://127.0.0.1:8189/api/v2/health",timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            if time.monotonic() > proxy_deadline:
                raise RuntimeError("Comfy SDK proxy startup timed out")
            time.sleep(.25)
        print("Comfy ready; submitting via official SDK", flush=True)
        sdk_result = run_with_sdk(graph, "/tmp/openjutsu-sdk-output", timeout=max(1,int(deadline-time.monotonic())))
        raw = sorted(Path(p) for p in sdk_result["files"] if Path(p).suffix.lower() == ".png")
        if len(raw) != frame_count:
            raise RuntimeError(f"Expected {frame_count} frames, received {len(raw)}")
        fixture = Path("/tmp/openjutsu-fixture")
        result = Path("/tmp/openjutsu-result")
        for folder in ("raw", "composite"):
            (result / folder).mkdir(parents=True, exist_ok=True)
        for i, file in enumerate(raw):
            generated = Image.open(file).convert("RGB")
            source = Image.open(fixture/"source"/f"{i:04d}.png").convert("RGB")
            mask = Image.open(fixture/"masks"/f"{i:04d}.png").convert("L")
            generated.save(result/"raw"/f"{i:04d}.png")
            # Explicit pixel preservation is compositing, not a model-quality claim.
            Image.composite(generated, source, mask).save(result/"composite"/f"{i:04d}.png")
        for label, source in (("source",fixture/"source"),("generated",result/"raw"),("composite",result/"composite")):
            subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(json.loads((fixture/"settings.json").read_text(encoding="utf-8")).get("fps",8)),"-i",str(source/"%04d.png"),
                            "-c:v","libx264","-crf","18","-pix_fmt","yuv420p",str(result/f"{label}.mp4")],
                           check=True, timeout=20)
        sheet = Image.new("RGB", (960, 1000), "white")
        draw = ImageDraw.Draw(sheet)
        for col,label in enumerate(("Source", "Raw model output", "Composite outside mask")):
            draw.text((col*320+8,8),label,fill="black")
        for row,i in enumerate((0,frame_count//2,frame_count-1)):
            for col,source in enumerate((fixture/"source",result/"raw",result/"composite")):
                from PIL import ImageOps
                with Image.open(source/f"{i:04d}.png") as frame:
                    thumb = ImageOps.pad(frame,(320,320),color=(232,232,232))
                    sheet.paste(thumb,(col*320,40+row*320))
        sheet.save(result/"comparison.jpg")
        metadata = {
            "status":"generated-unreviewed", "model":model_info["repo"],"model_revision":model_info["revision"],
            "mode":model_info["mode"],
            "comfy_commit":COMFY_COMMIT,"gpu":"L40S", "elapsed_seconds":round(time.monotonic()-start,2),
            "comfy_sdk":"0.5.0", "comfy_api_proxy":"0.1.6", "sdk_job_id":sdk_result["job_id"],
            "frames":frame_count,"fps":json.loads((fixture/"settings.json").read_text(encoding="utf-8")).get("fps",8),"width":width,"height":height,
            "seed":graph["9"]["inputs"]["seed"],"steps":graph["9"]["inputs"]["steps"],
            "input_provenance":model_info.get("input_provenance","original procedural drawings"),
            "target_erased_in_control":model_info["mode"] == "object-swap",
            "limitations":["Feasibility test; visual quality has not yet been reviewed.",
                            "Outside-mask pixel preservation in composite.mp4 comes from explicit compositing.",
                            "Does not prove general input quality or Genjutsu parity."],
        }
        (result/"manifest.json").write_text(json.dumps(metadata,indent=2))
        (result/"workflow-api.json").write_text(json.dumps(graph,indent=2))
        (result/"comfy.log").write_text(log_path.read_text())
        frozen = subprocess.check_output(["pip","freeze"],text=True)
        (result/"environment.txt").write_text(frozen)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as bundle:
            for folder,prefix in ((result,""),(fixture,"inputs/")):
                for file in sorted(folder.rglob("*")):
                    if file.is_file():
                        bundle.write(file,prefix+file.relative_to(folder).as_posix())
        return archive.getvalue()
    finally:
        if proxy is not None:
            proxy.terminate()
            try:
                proxy.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proxy.kill()
                proxy.wait(timeout=5)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        log.close()


@app.local_entrypoint()
def main(confirm_credits_only: bool = False):
    if not confirm_credits_only:
        raise RuntimeError("Verify remaining credits and $0 out-of-pocket cap, then pass --confirm-credits-only")
    payload = masked_replacement.remote()
    import datetime
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = HERE/"results"/stamp
    destination.mkdir(parents=True,exist_ok=False)
    (destination/"proof.zip").write_bytes(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for item in archive.infolist():
            target = (destination/item.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Archive member escaped result directory")
        archive.extractall(destination)
    print(f"Saved real generation for visual review: {destination}")
