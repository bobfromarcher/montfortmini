"""Experimental native multi-reference preparation for motion-transfer framing.

Recipe follows Comfy's FLUX.2 Klein 4B distilled two-image editing template.
This module is not enabled in production until paired quality checks pass.
"""
FILES=[
 ('black-forest-labs/FLUX.2-klein-4b-fp8','5b4408e59397a4a37ccb46afe426d8ed86379441','flux-2-klein-4b-fp8.safetensors','diffusion_models/flux-2-klein-4b-fp8.safetensors','97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6'),
 ('Comfy-Org/z_image_turbo','6fc90a3b1b653e935a0d175e260736de25b84df5','split_files/text_encoders/qwen_3_4b.safetensors','text_encoders/qwen_3_4b.safetensors','6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a'),
 ('Comfy-Org/vae-text-encorder-for-flux-klein-4b','5f526678002e43af5551dadb73ce2e8c91b43afe','split_files/vae/flux2-vae.safetensors','vae/flux2-vae.safetensors','868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3'),
]
PROMPT=('Replace the seated man in image 1 with the man from image 2, wearing his gold aviator sunglasses, '
        'black blazer and red floral open-collar shirt. Keep the face shape and wavy brown hair of image 2. '
        'Match image 1 body position, head direction, hand placement, camera framing, table and warm restaurant lighting. '
        'Preserve all restaurant objects and the seated posture. One adult man, natural anatomy, photorealistic.')
def build_graph(prompt=PROMPT,seed=42,width=768,height=1360):
 def n(kind,**inputs):return {'class_type':kind,'inputs':inputs}
 return {
  '1':n('UNETLoader',unet_name='flux-2-klein-4b-fp8.safetensors',weight_dtype='default'),
  '2':n('CLIPLoader',clip_name='qwen_3_4b.safetensors',type='flux2',device='default'),
  '3':n('VAELoader',vae_name='flux2-vae.safetensors'),
  '4':n('CLIPTextEncode',clip=['2',0],text=prompt),
  '5':n('ConditioningZeroOut',conditioning=['4',0]),
  '6':n('LoadImage',image='recovery-source.png'),
  '7':n('LoadImage',image='recovery-identity.png'),
  '8':n('VAEEncode',pixels=['6',0],vae=['3',0]),
  '9':n('VAEEncode',pixels=['7',0],vae=['3',0]),
  '10':n('ReferenceLatent',conditioning=['4',0],latent=['8',0]),
  '11':n('ReferenceLatent',conditioning=['10',0],latent=['9',0]),
  '12':n('ReferenceLatent',conditioning=['5',0],latent=['8',0]),
  '13':n('ReferenceLatent',conditioning=['12',0],latent=['9',0]),
  '14':n('EmptyFlux2LatentImage',width=width,height=height,batch_size=1),
  '15':n('RandomNoise',noise_seed=seed),
  '16':n('CFGGuider',model=['1',0],positive=['11',0],negative=['13',0],cfg=1.0),
  '17':n('KSamplerSelect',sampler_name='euler'),
  '18':n('Flux2Scheduler',steps=4,width=width,height=height),
  '19':n('SamplerCustomAdvanced',noise=['15',0],guider=['16',0],sampler=['17',0],sigmas=['18',0],latent_image=['14',0]),
  '20':n('VAEDecode',samples=['19',1],vae=['3',0]),
  '21':n('SaveImage',images=['20',0],filename_prefix='recovery-anchor'),
 }

if __name__=='__main__':
 from pathlib import Path
 from huggingface_hub import hf_hub_download
 import hashlib,shutil
 if not Path('/opt/ComfyUI/main.py').exists():raise RuntimeError('Remote model build only')
 for repo,rev,name,dest,expected in FILES:
  p=Path(hf_hub_download(repo,name,revision=rev,local_dir='/tmp/anchor-download'))
  h=hashlib.sha256()
  with p.open('rb') as f:
   while b:=f.read(8*1024*1024):h.update(b)
  if h.hexdigest()!=expected:raise RuntimeError('Digest mismatch: '+name)
  target=Path('/opt/ComfyUI/models')/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.move(p,target)
  print('Verified '+dest+' '+expected,flush=True)
