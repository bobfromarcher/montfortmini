"""Pinned alternative native recipe for the bounded quality-recovery experiment."""
from pathlib import Path
import hashlib,shutil
from huggingface_hub import hf_hub_download
FILES={
 'diffusion_models/wan_animate_2_int8_convrot.safetensors':'0580ecdd65e47e97c30df9670d13a6c4a131d26de5a1faf2ccc78392d5167584',
 'loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors':'85c4a61c30e0497aa44b91d93a893b624708461a56fe5485183b28fa07e2dfb3',
}
if __name__=='__main__':
 if not Path('/opt/ComfyUI/main.py').exists():raise RuntimeError('Remote image build only')
 for name,expected in FILES.items():
  p=Path(hf_hub_download('Comfy-Org/Wan-Animate-2',name,revision='e7181fe1896b7f2ce34120d1a3663413548240d7',local_dir='/tmp/recovery-models'))
  digest=hashlib.sha256()
  with p.open('rb') as f:
   while block:=f.read(8*1024*1024):digest.update(block)
  if digest.hexdigest()!=expected:raise RuntimeError('Model digest mismatch: '+name)
  target=Path('/opt/ComfyUI/models')/name;target.parent.mkdir(exist_ok=True,parents=True);shutil.move(p,target)
  print('Verified '+name+' '+expected,flush=True)
