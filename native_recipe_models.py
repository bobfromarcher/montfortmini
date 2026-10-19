"""Pinned assets referenced by the official native Wan Animate template."""
from pathlib import Path
import hashlib
import json

ASSETS = [
    {'repo': 'Kijai/WanVideo_comfy_fp8_scaled',
     'revision': '033a4e487f60220b3d6e469599a6aebc46e13cee',
     'file': 'Wan22Animate/Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors',
     'directory': 'diffusion_models', 'bytes': 18401760586,
     'sha256': '2936b31473a967e7a429a6646bba60e7862d0938e178b58b2a140f391dd5b8e6'},
    {'repo': 'Kijai/WanVideo_comfy',
     'revision': '8260d429d19fd7a72304cad059160b95d843913f',
     'file': 'Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors',
     'directory': 'loras', 'bytes': 738005744,
     'sha256': '85c4a61c30e0497aa44b91d93a893b624708461a56fe5485183b28fa07e2dfb3'},
    {'repo': 'Kijai/WanVideo_comfy',
     'revision': '8260d429d19fd7a72304cad059160b95d843913f',
     'file': 'LoRAs/Wan22_relight/WanAnimate_relight_lora_fp16.safetensors',
     'directory': 'loras', 'bytes': 1436672440,
     'sha256': 'fc646c74c73f4b251f5fd9bc440ef21b03b27305f499966c68b2b3aa31498561'},
]


def download():
    from huggingface_hub import hf_hub_download
    for asset in ASSETS:
        path = Path(hf_hub_download(asset['repo'], asset['file'], revision=asset['revision'],
                                   local_dir='/tmp/native-recipe-weights'))
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(8*1024*1024), b''):
                h.update(block)
        if path.stat().st_size != asset['bytes'] or h.hexdigest() != asset['sha256']:
            raise RuntimeError('Native recipe model integrity mismatch')
        target = Path('/opt/ComfyUI/models') / asset['directory'] / Path(asset['file']).name
        target.parent.mkdir(parents=True, exist_ok=True)
        path.replace(target)
        print(json.dumps({'asset': asset['file'], 'bytes': asset['bytes'], 'sha256': h.hexdigest()}), flush=True)


if __name__ == '__main__':
    download()
