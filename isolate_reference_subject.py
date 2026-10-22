"""Remove unrelated generated reference fragments using one detected subject mask."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np
from PIL import Image

MODEL_SHA = '4eaa5eb7a98365221087693fcc286334cf0858e2eb6e15b506aa4a7ecdcec4ad'


def isolate(reference, base, edit_mask, model, output):
    import mediapipe as mp
    if hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA:
        raise ValueError('Unexpected CPU segmentation model')
    with Image.open(reference) as im: generated = im.convert('RGB')
    with Image.open(base) as im: original = im.convert('RGB')
    with Image.open(edit_mask) as im: editable = np.asarray(im.convert('L')) > 0
    if generated.size != original.size or editable.shape != np.asarray(original).shape[:2]:
        raise ValueError('Different reference/mask dimensions')
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE, num_poses=1,
        min_pose_detection_confidence=.5, min_pose_presence_confidence=.5,
        output_segmentation_masks=True)
    # The Windows MediaPipe float-mask projection aborts for this650x750 input.
    # Keep the native graph on dimensions aligned to32; resample its CPU mask back.
    inference_size = tuple(max(32, round(n / 32) * 32) for n in generated.size)
    inference_image = generated.resize(inference_size, Image.Resampling.LANCZOS)
    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(inference_image)))
        if len(result.pose_landmarks) != 1 or len(result.segmentation_masks) != 1:
            raise ValueError('Primary reference person not uniquely detected')
        # Own the mask buffer before closing the native detector graph.
        alpha = np.squeeze(result.segmentation_masks[0].numpy_view()).copy()
    alpha = np.asarray(Image.fromarray(alpha).resize(generated.size, Image.Resampling.BILINEAR))
    if alpha.shape != editable.shape: raise ValueError('Unexpected mask shape')
    # Preserve the original registered reference outside the original edit mask.
    # Inside, retain generated pixels only where this one-person model places it.
    weight = np.clip(alpha, 0, 1)[..., None]
    g, b = np.asarray(generated), np.asarray(original)
    data = b.copy()
    data[editable] = np.rint(g * weight + b * (1 - weight)).astype('uint8')[editable]
    if not np.array_equal(data[~editable], b[~editable]): raise RuntimeError('Protected pixels changed')
    output.mkdir(parents=True, exist_ok=False)
    Image.fromarray(data).save(output / 'anchor.png')
    Image.fromarray(np.rint(alpha * 255).astype('uint8')).save(output / 'subject-mask.png')
    record = {'status': 'succeeded', 'failure': None,
              'candidate': 'Masked lower-body completion plus CPU primary-person isolation',
              'model_sha256': MODEL_SHA, 'mediapipe': mp.__version__, 'CPU_inference_size': inference_size,
              'input_reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
              'base_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
              'edit_mask_sha256': hashlib.sha256(edit_mask.read_bytes()).hexdigest(),
              'outside_edit_max_error': 0,
              'software_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'reference_landmarks': [{'x': p.x, 'y': p.y, 'visibility': p.visibility} for p in result.pose_landmarks[0]],
              'limits': ['Development amendment after failed reference generation; no new GPU reference sample.',
                         'Subject segmentation can erase or retain incorrect pixels; visual/video gates remain required.',
                         'No generated video pixel is replaced or composited by this helper.']}
    (output / 'manifest.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    with zipfile.ZipFile(output / 'reference-archive.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for name in ('anchor.png', 'subject-mask.png', 'manifest.json'): z.write(output / name, name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'base', 'edit-mask', 'model', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    isolate(args.reference, args.base, args.edit_mask, args.model, args.output)
