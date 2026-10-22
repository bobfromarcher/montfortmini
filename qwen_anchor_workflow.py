"""Pinned native Qwen-Image-Edit-2511 base recipe for reference-fidelity comparison."""
PROMPT=("Replace the person in image 1 with the character from image 2. "
 "Preserve the character's face shape, hair, clothing, colors and accessories from image 2. "
 "Keep the body position, head direction, hand positions, camera framing and perspective from image 1. "
 "Preserve the background, furniture, held objects and scene lighting from image 1. "
 "One character with natural anatomy, rendered in the visual style of image 2.")
FILES=[
 ('Comfy-Org/Qwen-Image-Edit_ComfyUI','f68ace85e60b4a02a323e394253731947657b7d2','split_files/diffusion_models/qwen_image_edit_2511_int8_convrot.safetensors','diffusion_models/qwen_image_edit_2511_int8_convrot.safetensors','11b5af5ac601821d73930c84846c9a158e67177356daf927ce1c8d10f3963829'),
 ('Comfy-Org/Qwen-Image_ComfyUI','1f12b17be14c89b026c51a91d67c32f84bb047bc','split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors','text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors','cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4'),
 ('Comfy-Org/Qwen-Image_ComfyUI','1f12b17be14c89b026c51a91d67c32f84bb047bc','split_files/vae/qwen_image_vae.safetensors','vae/qwen_image_vae.safetensors','a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'),
]
def build_graph(prompt=PROMPT,seed=42,width=768,height=1360):
 def n(kind,**inputs):return {'class_type':kind,'inputs':inputs}
 return {
  '1':n('UNETLoader',unet_name='qwen_image_edit_2511_int8_convrot.safetensors',weight_dtype='default'),
  '2':n('CLIPLoader',clip_name='qwen_2.5_vl_7b_fp8_scaled.safetensors',type='qwen_image',device='default'),
  '3':n('VAELoader',vae_name='qwen_image_vae.safetensors'),
  '4':n('LoadImage',image='recovery-source.png'),'5':n('LoadImage',image='recovery-identity.png'),
  '6':n('TextEncodeQwenImageEditPlus',clip=['2',0],vae=['3',0],image1=['4',0],image2=['5',0],prompt=prompt),
  '7':n('TextEncodeQwenImageEditPlus',clip=['2',0],vae=['3',0],image1=['4',0],image2=['5',0],prompt=''),
  '8':n('FluxKontextMultiReferenceLatentMethod',conditioning=['6',0],reference_latents_method='index_timestep_zero'),
  '9':n('FluxKontextMultiReferenceLatentMethod',conditioning=['7',0],reference_latents_method='index_timestep_zero'),
  '10':n('ModelSamplingAuraFlow',model=['1',0],shift=3.1),
  '11':n('CFGNorm',model=['10',0],strength=1.0,preserve_direction=False),
  '12':n('VAEEncode',pixels=['4',0],vae=['3',0]),
  '13':n('KSampler',model=['11',0],seed=seed,steps=40,cfg=4.0,sampler_name='euler',scheduler='simple',positive=['8',0],negative=['9',0],latent_image=['12',0],denoise=1.0),
  '14':n('VAEDecode',samples=['13',0],vae=['3',0]),
  '15':n('SaveImage',images=['14',0],filename_prefix='recovery-anchor'),
 }
if __name__=='__main__':
 from pathlib import Path
 from huggingface_hub import hf_hub_download
 import hashlib,shutil
 if not Path('/opt/ComfyUI/main.py').exists():raise RuntimeError('Remote model build only')
 for repo,rev,name,dest,expected in FILES:
  p=Path(hf_hub_download(repo,name,revision=rev,local_dir='/tmp/qwen-anchor-download'))
  h=hashlib.sha256()
  with p.open('rb') as f:
   while b:=f.read(8*1024*1024):h.update(b)
  if h.hexdigest()!=expected:raise RuntimeError('Digest mismatch: '+name)
  target=Path('/opt/ComfyUI/models')/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.move(p,target)
  print('Verified '+dest+' '+expected,flush=True)
