"""Original local VACE/Animate2 recipes, isolated from cloud orchestration.

The validated native Wan2.2 motion path lives in native_motion_backend.py.
This legacy Docker entrypoint makes no remote Modal calls.
"""
import base64
import io
import json
import zipfile
from modal_probe import masked_replacement


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
