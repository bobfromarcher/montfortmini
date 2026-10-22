"""Complete only missing reference-body regions; keep original upper pixels exact."""
from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image
import qwen_reference_alignment as qwen

PROMPT = (
    'Complete the missing lower body in image 1. The man currently ends abruptly at his thighs. '
    'Continue his existing charcoal trousers into two anatomically plausible legs that extend '
    'naturally through the bottom edge of this camera framing. Keep the same person, scale, '
    'waist and thigh positions, blue blazer, ivory shirt, trouser material and lighting. '
    'Image 2 supplies the same original character appearance. Keep all visible upper body, '
    'face, eyeglasses, hair, beard, arms and clothes unchanged. '
    'Plain neutral gray backdrop. One continuous adult body. No floating cutout, '
    'no duplicate legs, no extra people, no bicycle, no text and no new props.'
)


def body_mask(alpha, size, matrix):
    """Edit from a small overlap before the last observed body row, never the face."""
    inverse = np.linalg.inv(np.asarray(matrix, dtype=float))
    aligned = alpha.convert('L').transform(size, Image.Transform.AFFINE,
        tuple(inverse[:2].reshape(-1)), Image.Resampling.BICUBIC, fillcolor=0)
    foreground = np.asarray(aligned) >= 200
    rows = np.flatnonzero(foreground.any(axis=1))
    if len(rows) == 0:
        raise ValueError('No registered foreground')
    last = int(rows[-1])
    first_edit = last - max(8, round(size[1] * .025))
    if not .55 * size[1] < first_edit < .94 * size[1]:
        raise ValueError('Missing body boundary is not in the supported lower image region')
    mask = np.zeros((size[1], size[0]), dtype='uint8')
    mask[first_edit:] = 255
    return Image.fromarray(mask), {'last_observed_body_row': last, 'first_edit_row': first_edit,
                                    'editable_fraction': float((mask > 0).mean())}


def protect(base, generated, mask):
    """Only reference preparation is composited; generated video is never patched."""
    if base.size != mask.size:
        raise ValueError('Reference protection mask dimensions differ')
    raw = generated.convert('RGB').resize(base.size, Image.Resampling.LANCZOS)
    result = Image.composite(raw, base.convert('RGB'), mask.convert('L'))
    outside = np.asarray(mask) == 0
    if not np.array_equal(np.asarray(result)[outside], np.asarray(base.convert('RGB'))[outside]):
        raise RuntimeError('Protected reference pixels changed')
    return result, raw


@contextmanager
def masked_policy(mask_path):
    builder = qwen.build_graph
    def build(*args, **kwargs):
        graph = builder(*args, **kwargs)
        graph['16'] = {'class_type': 'LoadImageMask', 'inputs': {'image': mask_path.name, 'channel': 'red'}}
        graph['17'] = {'class_type': 'SetLatentNoiseMask',
                       'inputs': {'samples': ['12', 0], 'mask': ['16', 0]}}
        graph['13']['inputs']['latent_image'] = ['17', 0]
        return graph
    try:
        qwen.build_graph = build
        yield
    finally:
        qwen.build_graph = builder


def run_reference(bundle, identity):
    with zipfile.ZipFile(io.BytesIO(bundle)) as z:
        base_bytes, mask_bytes = z.read('base.png'), z.read('edit-mask.png')
        preparation = json.loads(z.read('preparation.json'))
    if hashlib.sha256(identity).hexdigest() != preparation['identity_sha256']:
        raise ValueError('Identity does not match frozen reference bundle')
    with Image.open(io.BytesIO(base_bytes)) as im: base = im.convert('RGB')
    with Image.open(io.BytesIO(mask_bytes)) as im: mask = im.convert('L')
    if base.size != mask.size or not set(np.unique(mask)).issubset({0, 255}):
        raise ValueError('Invalid binary lower-body mask')
    target = Path('/opt/ComfyUI/input'); target.mkdir(parents=True, exist_ok=True)
    path = target / 'protected-fill-mask.png'
    mask.resize(qwen.source_canvas(*base.size), Image.Resampling.NEAREST).save(path)
    with masked_policy(path):
        data = qwen.run_reference_alignment(base_bytes, identity, prompt=PROMPT,
                                            output_directory='/tmp/protected-reference-stage')
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as stage, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as out:
        manifest = json.loads(stage.read('manifest.json'))
        for item in stage.infolist():
            if not item.is_dir(): out.writestr('qwen/' + item.filename, stage.read(item))
        if manifest['status'] == 'succeeded':
            with Image.open(io.BytesIO(stage.read('anchor.png'))) as im:
                result, raw = protect(base, im, mask)
            for name, image in [('anchor.png', result), ('raw-reference-resized.png', raw)]:
                stream = io.BytesIO(); image.save(stream, format='PNG'); out.writestr(name, stream.getvalue())
        out.writestr('base.png', base_bytes); out.writestr('edit-mask.png', mask_bytes)
        out.writestr('conditioning-mask.png', path.read_bytes())
        out.writestr('preparation.json', json.dumps(preparation, indent=2))
        out.writestr('manifest.json', json.dumps({
            'status': manifest['status'], 'failure': manifest['failure'],
            'candidate': 'Masked lower-body Qwen completion with exact upper-reference pixel protection',
            'original_identity_sha256': hashlib.sha256(identity).hexdigest(),
            'base_sha256': hashlib.sha256(base_bytes).hexdigest(),
            'mask_sha256': hashlib.sha256(mask_bytes).hexdigest(), 'stage': manifest,
            'protected_reference_outside_mask_max_error': 0 if manifest['status'] == 'succeeded' else None,
            'software_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limitations': ['Original upper pose/head direction remain unchanged.',
                           'Synthetic missing-body completion, not recovery of a real hidden body.',
                           'Exact pixel protection applies to the prepared reference only, not generated video.',
                           'Does not identify Genjutsu implementation or establish video quality.']}, indent=2))
    return output.getvalue()
