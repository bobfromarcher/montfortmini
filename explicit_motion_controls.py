"""CPU-only source controls for the older Wan2.2-Animate native conditioning node.

MediaPipe body estimates are mapped to OpenPose18. This is not DWPose133 and
does not claim detailed finger control. Source RGB enters only the face branch.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import zipfile
import numpy as np
from PIL import Image
from pose_guide import to_openpose, draw_pose


def face_box(points, size):
    width, height = size
    face = [points[i] for i in range(11) if points[i]['visibility'] >= .5]
    if len(face) < 5:
        raise ValueError('Insufficient visible face landmarks; do not synthesize a face control')
    xs, ys = [p['x'] * width for p in face], [p['y'] * height for p in face]
    side = max(max(xs)-min(xs), (max(ys)-min(ys))*1.5) * 1.35
    if not 16 <= side <= min(size)*.7:
        raise ValueError('Unreliable face box')
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    return tuple(round(v) for v in (cx-side/2, cy-side/2, cx+side/2, cy+side/2))


def prepare(fixture, model, output):
    import mediapipe as mp
    started = time.monotonic()
    cfg = json.loads((fixture/'settings.json').read_text())
    source = sorted((fixture/'source').glob('*.png'))
    if len(source) != cfg['frames']:
        raise ValueError('Actual source length differs from frozen fixture')
    output.mkdir(parents=True, exist_ok=False)
    for name in ('source','masks','pose','face'):
        (output/name).mkdir()
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO, num_poses=1,
        min_pose_detection_confidence=.5, min_pose_presence_confidence=.5,
        min_tracking_confidence=.5)
    rows, arrays = [], {'source': [], 'mask': [], 'pose': [], 'face': []}
    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        for i, path in enumerate(source):
            im = Image.open(path).convert('RGB')
            pixels = np.asarray(im)
            result = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=pixels), i*125)
            if len(result.pose_landmarks) != 1:
                raise RuntimeError(f'No unique pose at frame{i}; stop before GPU')
            points = [{'x': float(p.x), 'y': float(p.y), 'z': float(p.z),
                       'visibility': float(p.visibility), 'presence': float(p.presence)}
                      for p in result.pose_landmarks[0]]
            joints = to_openpose(points)
            if any(joints[j]['visibility'] < .5 for j in (0,1,2,3,4,5,6,7)):
                raise RuntimeError(f'Low-confidence upper-body joint at frame{i}; inspect before GPU')
            pose = draw_pose(joints, im.size)
            box = face_box(points, im.size)
            face = im.crop(box).resize((256,256), Image.Resampling.BICUBIC)
            mask = Image.open(fixture/'masks'/path.name).convert('L')
            for name, image in [('source',im),('masks',mask),('pose',pose),('face',face)]:
                image.save(output/name/path.name)
            for name, image in [('source',im),('mask',mask),('pose',pose),('face',face)]:
                arrays[name].append(np.asarray(image,dtype=np.float32)/255)
            rows.append({'frame': i, 'timestamp_ms':i*125, 'face_box_xyxy':box,
                         'mediapipe33':points, 'openpose18':joints})
    reference = Image.open(fixture/'reference.png').convert('RGB')
    reference.save(output/'reference.png')
    arrays = {k: np.stack(v) for k,v in arrays.items()}
    arrays['reference'] = np.asarray(reference,dtype=np.float32)/255
    np.savez_compressed(output/'conditioning.npz', **arrays)
    (output/'settings.json').write_text(json.dumps(cfg,indent=2))
    (output/'controls.json').write_text(json.dumps({
        'method':'MediaPipe0.10.35 FullPose VIDEO → OpenPose18 body, no hand/face mesh',
        'limitations':'Estimated controls, not ground truth; no detailed fingers; face crop includes source appearance. No retargeting or temporal smoothing.',
        'elapsed_cpu_seconds':time.monotonic()-started,
        'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
        'source_frame_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source},
        'prepared_reference_sha256':hashlib.sha256((fixture/'reference.png').read_bytes()).hexdigest(),
        'frames':rows},indent=2))
    with zipfile.ZipFile(output/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(output.rglob('*')):
            if p.is_file() and p.name != 'inputs.zip':z.write(p,p.relative_to(output).as_posix())


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('fixture','model','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();prepare(args.fixture,args.model,args.output)
