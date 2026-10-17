from workflow import build_graph as build_vace
from motion_model_config import MODEL_FILES


def build_graph():
    graph = build_vace(steps=10)
    graph["1"]["inputs"]["unet_name"] = MODEL_FILES["diffusion_models"]
    graph["4"]["inputs"]["text"] = (
        "A friendly illustrated young man with orange brown hair and a blue shirt raises his right arm to wave. "
        "Full body, fixed camera, simple beige studio backdrop, stable character appearance.")
    graph["5"]["inputs"]["text"] = "distorted hands, extra limbs, text, watermark, flicker"
    graph["6"] = {"class_type":"OpenJutsuMotionInputs","inputs":{}}
    graph["13"] = {"class_type":"CLIPVisionLoader","inputs":{"clip_name":MODEL_FILES["clip_vision"]}}
    graph["14"] = {"class_type":"CLIPVisionEncode","inputs":{"clip_vision":["13",0],"image":["6",1],"crop":"none"}}
    graph["15"] = {"class_type":"ImageFromBatch","inputs":{"image":["6",0],"batch_index":0,"length":1}}
    graph["16"] = {"class_type":"CLIPVisionEncode","inputs":{"clip_vision":["13",0],"image":["15",0],"crop":"none"}}
    graph["7"] = {"class_type":"WanAnimate2ToVideo","inputs":{
        "positive":["4",0],"negative":["5",0],"vae":["3",0],
        "width":320,"height":320,"length":17,"batch_size":1,"video_frame_offset":0,
        "pose_strength":1.0,"pose_start_percent":0.0,"pose_end_percent":1.0,"reference_image_strength":1.0,
        "reference_image":["6",1],"pose_video":["6",0],"clip_vision_output":["14",0],"clip_vision_output_pose":["16",0]}}
    graph["8"]["inputs"]["shift"] = 5.0
    graph["9"]["inputs"].update(cfg=1.0,sampler_name="lcm",scheduler="simple")
    return graph
