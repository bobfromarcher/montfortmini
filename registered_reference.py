"""Register original subject pixels to source torso framing; no image-generation stage."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

JOINTS = (11, 12, 23, 24)
POSE_MODEL_SHA = '4eaa5eb7a98365221087693fcc286334cf0858e2eb6e15b506aa4a7ecdcec4ad'


def similarity(source_points, destination_points):
    """Least-squares uniform scale+rotation+translation, never a mirror or face squeeze."""
    x, y = np.asarray(source_points, dtype=float), np.asarray(destination_points, dtype=float)
    xc, yc = x - x.mean(0), y - y.mean(0)
    u, s, vt = np.linalg.svd(xc.T @ yc)
    signs = np.array([1., 1. if np.linalg.det(u @ vt) > 0 else -1.])
    rotation = u @ np.diag(signs) @ vt
    scale = float(np.sum(s * signs) / np.sum(xc * xc))
    if not .02 < scale < 8:
        raise ValueError('Unsupported registration scale')
    translation = y.mean(0) - scale * x.mean(0) @ rotation
    matrix = np.eye(3)
    matrix[:2, :2] = scale * rotation.T
    matrix[:2, 2] = translation
    return matrix


def prepare(source, identity, source_landmarks, model, output):
    import mediapipe as mp
    if hashlib.sha256(model.read_bytes()).hexdigest() != POSE_MODEL_SHA:
        raise ValueError('Pose model hash changed')
    source_meta = json.loads(source_landmarks.read_text(encoding='utf-8'))
    if hashlib.sha256(source.read_bytes()).hexdigest() != source_meta['source_sha256']:
        raise ValueError('Source landmarks belong to another frame')
    with Image.open(source) as im:
        source_image = ImageOps.exif_transpose(im).convert('RGB')
    with Image.open(identity) as im:
        original = ImageOps.exif_transpose(im).convert('RGB')
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_poses=1, min_pose_detection_confidence=.5, min_pose_presence_confidence=.5,
        output_segmentation_masks=True)
    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(original)))
    if len(result.pose_landmarks) != 1 or len(result.segmentation_masks) != 1:
        raise ValueError('No reliable reference subject/mask; stop before GPU')
    points = [{'x': float(p.x), 'y': float(p.y), 'visibility': float(p.visibility)} for p in result.pose_landmarks[0]]
    if any(min(points[i]['visibility'], source_meta['mediapipe33'][i]['visibility']) < .5 for i in JOINTS):
        raise ValueError('Unreliable torso registration; stop before GPU')
    x = np.array([[points[i]['x'] * original.width, points[i]['y'] * original.height] for i in JOINTS])
    y = np.array([[source_meta['mediapipe33'][i]['x'] * source_image.width,
                   source_meta['mediapipe33'][i]['y'] * source_image.height] for i in JOINTS])
    matrix = similarity(x, y)
    projected = (matrix @ np.column_stack([x, np.ones(len(x))]).T).T[:, :2]
    errors = np.linalg.norm(projected-y, axis=1) / np.hypot(*source_image.size)
    if errors.max() > .06:
        raise ValueError('Torso calibration exceeds prospective geometric tolerance')
    mask = np.clip(result.segmentation_masks[0].numpy_view(), 0, 1)
    if mask.ndim == 3 and mask.shape[2] == 1:
        mask = mask[:, :, 0]
    if mask.shape != (original.height, original.width):
        raise ValueError('Unexpected reference mask geometry')
    alpha = Image.fromarray(np.rint(mask * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.8))
    rgba = original.convert('RGBA'); rgba.putalpha(alpha)
    inverse = np.linalg.inv(matrix)
    transformed = rgba.transform(source_image.size, Image.Transform.AFFINE,
                                 tuple(inverse[:2].reshape(-1)), Image.Resampling.BICUBIC,
                                 fillcolor=(0, 0, 0, 0))
    border = np.asarray(original)
    background = tuple(int(v) for v in np.median(np.concatenate([border[0], border[-1], border[:, 0], border[:, -1]]), axis=0).astype('uint8'))
    canvas = Image.new('RGBA', source_image.size, background + (255,))
    canvas = Image.alpha_composite(canvas, transformed).convert('RGB')
    output.mkdir(parents=True, exist_ok=False)
    canvas.save(output/'anchor.png'); alpha.save(output/'identity-mask.png')
    (output/'identity-original.png').write_bytes(identity.read_bytes())
    overlay = canvas.copy(); draw = ImageDraw.Draw(overlay)
    for point, target in zip(projected, y):
        a, b = tuple(point), tuple(target)
        draw.line((a, b), fill='yellow', width=2)
        draw.ellipse((b[0]-4, b[1]-4, b[0]+4, b[1]+4), fill='red')
    overlay.save(output/'torso-overlay.png')
    record = {'status': 'succeeded', 'failure': None,
              'candidate': 'Original pixels, torso similarity registration + reference-person segmentation; no Qwen/Klein',
              'original_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'original_identity_sha256': hashlib.sha256(identity.read_bytes()).hexdigest(),
              'pose_model_sha256': POSE_MODEL_SHA, 'mediapipe': mp.__version__,
              'matrix': matrix.tolist(), 'torso_errors_diagonal_fraction': errors.tolist(),
              'background_rgb': [int(v) for v in background], 'reference_landmarks': points,
              'software_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations': ['Uniform2D registration preserves original pose; no arm retargeting or3D head rotation.',
                             'Unseen body regions are not reconstructed. Mask/border resampling is explicit preprocessing.',
                             'No generated output pixels are replaced; raw video remains wholly model-generated.',
                             'Registration/error checks do not establish video fidelity, motion or temporal success.']}
    (output/'manifest.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    with zipfile.ZipFile(output/'reference-archive.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for p in output.iterdir():
            if p.is_file() and p.suffix != '.zip':
                z.write(p, p.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'identity', 'source-landmarks', 'model', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.identity, args.source_landmarks, args.model, args.output)
