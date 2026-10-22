"""Appearance-free pose conditioning. Optional CPU preprocessing, no generation API."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# COCO/OpenPose18 joint order mapped from MediaPipe33. Neck is shoulder midpoint.
MAPPING = [0, None, 12, 14, 16, 11, 13, 15, 24, 26, 28, 23, 25, 27, 5, 2, 8, 7]
LIMBS = [(1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7),
         (1, 8), (8, 9), (9, 10), (1, 11), (11, 12), (12, 13),
         (1, 0), (0, 14), (14, 16), (0, 15), (15, 17)]
COLORS = [(255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0),
          (170, 255, 0), (85, 255, 0), (0, 255, 0), (0, 255, 85),
          (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
          (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255),
          (255, 0, 170), (255, 0, 85)]


def to_openpose(landmarks):
    if len(landmarks) != 33:
        raise ValueError('Expected one MediaPipe33 pose')
    joints = [dict(landmarks[i]) if i is not None else None for i in MAPPING]
    a, b = landmarks[11], landmarks[12]
    joints[1] = {'x': (a['x'] + b['x']) / 2, 'y': (a['y'] + b['y']) / 2,
                 'visibility': min(a['visibility'], b['visibility'])}
    return joints


def draw_pose(joints, size, threshold=0.5):
    """Never invent out-of-frame/low-confidence joints or carry source RGB pixels."""
    width, height = size
    canvas = Image.new('RGB', size, 'black')
    draw = ImageDraw.Draw(canvas)
    radius = max(3, round(min(size) / 150))
    def point(i):
        p = joints[i]
        if p['visibility'] < threshold or not (0 <= p['x'] < 1 and 0 <= p['y'] < 1):
            return None
        return round(p['x'] * (width - 1)), round(p['y'] * (height - 1))
    for i, (a, b) in enumerate(LIMBS):
        pa, pb = point(a), point(b)
        if pa is not None and pb is not None:
            draw.line((pa, pb), fill=COLORS[i], width=radius * 2)
    for i in range(18):
        p = point(i)
        if p is not None:
            x, y = p
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=COLORS[i])
    return canvas


def extract(source, model, output):
    import mediapipe as mp
    with Image.open(source) as im:
        rgb = np.asarray(ImageOps.exif_transpose(im).convert('RGB'))
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE, num_poses=1,
        min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5)
    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if len(result.pose_landmarks) != 1:
        raise RuntimeError('No reliable pose; no reference inference allowed')
    landmarks = [{'x': float(p.x), 'y': float(p.y), 'z': float(p.z),
                  'visibility': float(p.visibility), 'presence': float(p.presence)}
                 for p in result.pose_landmarks[0]]
    joints = to_openpose(landmarks)
    # Visible upper body is essential; invisible lower joints remain absent.
    if any(joints[i]['visibility'] < .5 for i in (0, 1, 2, 3, 5, 6, 8, 11)):
        raise RuntimeError('Unreliable principal pose landmarks; stop before GPU')
    output.mkdir(parents=True, exist_ok=False)
    draw_pose(joints, (rgb.shape[1], rgb.shape[0])).save(output / 'pose-guide.png')
    (output / 'landmarks.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
        'model_package': 'mediapipe==' + mp.__version__,
        'mediapipe33': landmarks, 'openpose18': joints,
        'visibility_threshold': .5,
        'limits': 'CPU detector estimates, not annotated ground truth. 2D body landmarks do not encode detailed fingers, clothing, source face texture or exact 3D head orientation.'}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    extract(args.source, args.model, args.output)
