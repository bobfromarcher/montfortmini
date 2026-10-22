"""Official pinned Wan whole-body control preparation, single-person CPU mode."""
import hashlib,io,json,sys,time,zipfile
from pathlib import Path

HERE=Path(__file__).parent

def download():
    from concurrent.futures import ThreadPoolExecutor
    from huggingface_hub import hf_hub_download
    manifest=json.loads((HERE/'vendor/wan_animate/provenance.json').read_text())
    def fetch(item):
        p=Path(hf_hub_download(manifest['pose_repo'],item['rfilename'],revision=manifest['pose_revision'],local_dir='/opt/upstream-pose'))
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if p.stat().st_size!=item['size'] or h!=item['lfs']['sha256']:raise ValueError('Pose weight integrity mismatch')
    with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(fetch,manifest['files']))
    print('All394 pinned whole-body ONNX files verified',flush=True)


def prepare(inputs):
    import cv2
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(HERE/'vendor/wan_animate'))
    from pose2d import Pose2d
    from pose2d_utils import AAPoseMeta
    from human_visualization import draw_aapose_by_meta_new
    from face_bbox import get_face_bboxes
    start=time.monotonic();root=Path('/tmp/upstream-input');root.mkdir(exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(inputs)) as z:
        if any(not (root/i.filename).resolve().is_relative_to(root) for i in z.infolist()):raise ValueError('Unsafe input archive')
        z.extractall(root)
    # This already-cropped development fixture contains exactly one person.
    # Upstream Pose2d explicitly supports detector=None/full-image bounding box.
    pose=Pose2d('/opt/upstream-pose/process_checkpoint/pose2d/vitpose_h_wholebody.onnx',detector_checkpoint=None,device='cpu')
    paths=sorted((root/'source').glob('*.png'))
    frames=[np.asarray(Image.open(p).convert('RGB')) for p in paths]
    metas=pose(frames);poses=[];faces=[];rows=[]
    for i,(im,meta) in enumerate(zip(frames,metas)):
        data=AAPoseMeta.from_humanapi_meta(meta)
        canvas=draw_aapose_by_meta_new(np.zeros_like(im),data)
        x1,x2,y1,y2=get_face_bboxes(meta['keypoints_face'][:,:2],scale=1.3,image_shape=im.shape[:2])
        if x2<=x1 or y2<=y1:raise ValueError('Invalid upstream face crop')
        face=cv2.resize(im[y1:y2,x1:x2],(512,512))
        Image.fromarray(canvas).save(root/'pose'/f'{i:04d}.png')
        Image.fromarray(face).save(root/'face'/f'{i:04d}.png')
        poses.append(canvas.astype(np.float32)/255);faces.append(face.astype(np.float32)/255)
        rows.append({'frame':i,'face_box':[x1,y1,x2,y2],**{k:v.tolist() for k,v in meta.items() if k.startswith('keypoints_')}})
    with np.load(root/'conditioning.npz',allow_pickle=False) as old:arrays={k:old[k].copy() for k in old.files}
    arrays.update(pose=np.stack(poses),face=np.stack(faces));np.savez_compressed(root/'conditioning.npz',**arrays)
    (root/'controls.json').write_text(json.dumps({'method':'pinned upstream ViTPose133 CPU/full-image detector=None; official v2 body+hands renderer and face-landmark crop; no retargeting','elapsed_cpu_seconds':time.monotonic()-start,'frames':rows},indent=2))
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for p in root.rglob('*'):
            if p.is_file() and p.name!='inputs.zip':z.write(p,p.relative_to(root).as_posix())
    return output.getvalue()


if __name__=='__main__':download()
