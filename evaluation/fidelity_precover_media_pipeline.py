"""Bounded user-media preparation for both independent editing workflows."""
import base64
import binascii
import json
import math
from pathlib import Path

MAX_VIDEO_BYTES = 12 * 1024 * 1024
MAX_IMAGE_BYTES = 4 * 1024 * 1024


def validate_payload(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a generation request")
    mode = data.get("mode")
    if mode not in ("object-swap", "motion-transfer"):
        raise ValueError("Choose Object swap or Motion transfer")
    frames = data.get("frames",17)
    if type(frames) is not int or frames not in (17,33):
        raise ValueError("Choose 17 or 33 frames")
    seed = data.get("seed",42)
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise ValueError("Seed must be between 0 and 2147483647")
    prompt = data.get("prompt","")
    if not isinstance(prompt,str) or len(prompt) > 2000:
        raise ValueError("Keep the prompt under 2000 characters")
    for field,limit in (("video_b64",MAX_VIDEO_BYTES),("reference_b64",MAX_IMAGE_BYTES)):
        value = data.get(field)
        if not isinstance(value,str) or not value or len(value) > (limit+2)//3*4:
            raise ValueError(f"{field.split('_')[0].title()} file exceeds its size limit or is missing")
        try:
            decoded = base64.b64decode(value,validate=True)
        except (ValueError,binascii.Error):
            raise ValueError("Invalid uploaded file data") from None
        if not decoded or len(decoded) > limit:
            raise ValueError("Uploaded file exceeds its size limit")
    default = [.2,.2,.6,.6]
    boxes = []
    for key in ("bbox","end_bbox"):
        box = data.get(key,data.get("bbox",default))
        if not isinstance(box,list) or len(box)!=4:
            raise ValueError("Replacement region must have four coordinates")
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in box):
            raise ValueError("Invalid replacement-region coordinates")
        x,y,w,h = box
        if not (0<=x<1 and 0<=y<1 and .02<=w<=1 and .02<=h<=1 and x+w<=1.000001 and y+h<=1.000001):
            raise ValueError("Replacement region must stay inside the frame")
        boxes.append([float(v) for v in box])
    return {"mode":mode,"frames":frames,"seed":seed,"prompt":prompt.strip(),
            "bbox":boxes[0],"end_bbox":boxes[1],
            "video_b64":data["video_b64"],"reference_b64":data["reference_b64"]}


def display_geometry(stream):
    """Match ffmpeg/browser display orientation rather than encoded pixel order."""
    width,height=stream["width"],stream["height"]
    rotation=0.0
    for side in stream.get("side_data_list",[]):
        if "rotation" in side:
            rotation=float(side["rotation"])
            break
    else:
        rotation=float(stream.get("tags",{}).get("rotate",0))
    if not math.isfinite(rotation) or abs(rotation/90-round(rotation/90))>0.001:
        raise ValueError("Use a video with a standard 90-degree display rotation")
    if round(rotation/90)%2:
        width,height=height,width
    return width,height


def prepare_media(data, *, max_side=480, target_short_side=None, fps=8):
    import shutil
    import subprocess
    from PIL import Image, ImageDraw, ImageOps

    data = validate_payload(data)
    root = Path("/tmp/openjutsu-fixture")
    shutil.rmtree(root,ignore_errors=True)
    for folder in ("source","masks"):
        (root/folder).mkdir(parents=True,exist_ok=True)
    video = root/"uploaded-video"
    video.write_bytes(base64.b64decode(data["video_b64"],validate=True))
    reference = root/"uploaded-reference"
    reference.write_bytes(base64.b64decode(data["reference_b64"],validate=True))
    probe = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                            "-show_entries","stream=width,height:stream_tags=rotate:stream_side_data=rotation","-of","json",str(video)],
                           capture_output=True,text=True,timeout=15,check=True)
    streams = json.loads(probe.stdout).get("streams",[])
    if not streams:
        raise ValueError("The video contains no readable video stream")
    original_w,original_h = display_geometry(streams[0])
    if original_w*original_h > 16_777_216 or min(original_w,original_h) <16:
        raise ValueError("Use a video up to 4K for this prototype")
    if max_side not in (480,864) or fps not in (8,16,24):
        raise ValueError("Unsupported internal preparation profile")
    scale = min(max_side/original_w,max_side/original_h)
    if target_short_side is not None:
        if target_short_side!=480:raise ValueError("Unsupported motion short-side size")
        scale=min(scale,target_short_side/min(original_w,original_h))
    width = min(max_side,max(128,round(original_w*scale/16)*16))
    height = min(max_side,max(128,round(original_h*scale/16)*16))
    frames = data["frames"]
    fit = min(width/original_w,height/original_h)
    fitted_w = max(2,int(original_w*fit)//2*2)
    fitted_h = max(2,int(original_h*fit)//2*2)
    pad_x,pad_y = (width-fitted_w)//2,(height-fitted_h)//2
    filt = f"fps={fps},scale={fitted_w}:{fitted_h},pad={width}:{height}:{pad_x}:{pad_y}:color=gray"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(video),"-an","-vf",filt,
                    "-frames:v",str(frames),"-start_number","0",str(root/"source"/"%04d.png")],
                   capture_output=True,timeout=30,check=True)
    decoded = sorted((root/"source").glob("*.png"))
    if not decoded:
        raise ValueError("The video could not be decoded")
    for i in range(len(decoded),frames):
        shutil.copyfile(decoded[-1],root/"source"/f"{i:04d}.png")
    Image.MAX_IMAGE_PIXELS = 16_777_216
    with Image.open(reference) as image:
        if image.width*image.height >16_777_216:
            raise ValueError("Use a reference image under 16 megapixels")
        reference_image = ImageOps.pad(ImageOps.exif_transpose(image).convert("RGB"),(width,height),color=(128,128,128))
        reference_image.save(root/"reference.png")
    for i in range(frames):
        mask = Image.new("L",(width,height),255 if data["mode"]=="motion-transfer" else 0)
        if data["mode"]=="object-swap":
            t = i/(frames-1)
            x,y,w,h = [a*(1-t)+b*t for a,b in zip(data["bbox"],data["end_bbox"])]
            ImageDraw.Draw(mask).rectangle((round(pad_x+x*fitted_w),round(pad_y+y*fitted_h),
                                            min(width-1,round(pad_x+(x+w)*fitted_w)),
                                            min(height-1,round(pad_y+(y+h)*fitted_h))),fill=255)
        mask.save(root/"masks"/f"{i:04d}.png")
    (root/"settings.json").write_text(json.dumps({"mode":data["mode"],"frames":frames,
                                                "width":width,"height":height,
                                                "display_width":original_w,"display_height":original_h}))
    return {**data,"width":width,"height":height,"root":str(root)}


def erase_target(source, mask):
    """VACE must not receive original target pixels through its reactive branch."""
    return source*(1-mask[...,None])+.5*mask[...,None]


class OpenJutsuMediaInputs:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{}}
    RETURN_TYPES = ("IMAGE","MASK","IMAGE")
    FUNCTION = "load"
    CATEGORY = "OpenJutsu/media"

    def load(self):
        import numpy as np
        import torch
        from PIL import Image
        root = Path("/tmp/openjutsu-fixture")
        settings = json.loads((root/"settings.json").read_text())
        frames = settings["frames"]
        def read(path,mode):
            with Image.open(path) as image:
                return np.asarray(image.convert(mode),dtype=np.float32)/255
        source = np.stack([read(root/"source"/f"{i:04d}.png","RGB") for i in range(frames)])
        mask = np.stack([read(root/"masks"/f"{i:04d}.png","L") for i in range(frames)])
        if settings["mode"]=="object-swap":
            source = erase_target(source,mask)
        ref = read(root/"reference.png","RGB")
        return torch.from_numpy(source),torch.from_numpy(mask),torch.from_numpy(ref)[None]


NODE_CLASS_MAPPINGS = {"OpenJutsuMediaInputs":OpenJutsuMediaInputs}
