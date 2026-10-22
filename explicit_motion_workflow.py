"""Frozen Wan2.2-Animate14B base experiment, explicit body and face controls."""
from workflow import build_graph as baseline_graph

MODEL_REPO='Comfy-Org/Wan_2.2_ComfyUI_Repackaged'
MODEL_REVISION='ee6f4a40737a995bf5818954cfce6d59443b0f04'
MODEL_FILE='wan2.2_animate_14B_bf16.safetensors'
MODEL_SHA256='7d37cb0120488dec2a061135aa3018426925318a60838c3de935c829abc88667'
MODEL_BYTES=34549787368


def build_graph(width=480,height=560,frames=33,face=True):
    graph=baseline_graph()
    graph['1']['inputs'].update(unet_name=MODEL_FILE,weight_dtype='default')
    graph['4']['inputs']['text']='The person in the reference image performs the movements from the source video. Stable appearance, natural motion, fixed camera.'
    graph['5']['inputs']['text']='text, watermark, flicker, distorted shapes, extra limbs, duplicate subjects'
    graph['6']={'class_type':'OpenJutsuExplicitInputs','inputs':{}}
    graph['13']={'class_type':'CLIPVisionLoader','inputs':{'clip_name':'clip_vision_h.safetensors'}}
    graph['14']={'class_type':'CLIPVisionEncode','inputs':{'clip_vision':['13',0],'image':['6',2],'crop':'none'}}
    graph['7']={'class_type':'WanAnimateToVideo','inputs':{
        'positive':['4',0],'negative':['5',0],'vae':['3',0],
        'width':width,'height':height,'length':frames,'batch_size':1,
        'reference_image':['6',2],'clip_vision_output':['14',0],
        'pose_video':['6',3],'continue_motion_max_frames':5,'video_frame_offset':0}}
    if face:graph['7']['inputs']['face_video']=['6',4]
    # Upstream base configuration: 20 steps, shift5, CFG1, no acceleration LoRA.
    # Comfy dpmpp_2m/simple is a comparable solver, not bit-exact upstream DPM++.
    graph['8']['inputs']['shift']=5.0
    graph['9']['inputs'].update(seed=42,steps=20,cfg=1.0,sampler_name='dpmpp_2m',scheduler='simple')
    return graph


def download():
    import hashlib,json
    from pathlib import Path
    from huggingface_hub import hf_hub_download
    path=Path(hf_hub_download(MODEL_REPO,'split_files/diffusion_models/'+MODEL_FILE,
                            revision=MODEL_REVISION,local_dir='/tmp/explicit-weights'))
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    if path.stat().st_size != MODEL_BYTES or h.hexdigest()!=MODEL_SHA256:
        raise RuntimeError('Pinned model integrity mismatch')
    target=Path('/opt/ComfyUI/models/diffusion_models')/MODEL_FILE
    target.parent.mkdir(parents=True,exist_ok=True)
    path.replace(target)
    print(json.dumps({'model':MODEL_FILE,'sha256':h.hexdigest(),'bytes':target.stat().st_size}),flush=True)


if __name__=='__main__':download()
