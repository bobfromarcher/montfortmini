"""One-factor identity-detail correction around the retained native editors."""
from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import zipfile

from identity_detail import identity_canvas
import reference_alignment as klein
import qwen_reference_alignment as qwen
from cascade_reference_alignment import run_reference_alignment as frozen_cascade


@contextmanager
def detail_policy(placement):
    if placement not in ('qwen', 'both'):
        raise ValueError('Choose the registered Qwen-only or both-stage ablation')
    modules = [qwen] if placement == 'qwen' else [klein, qwen]
    saved = [(module, module.identity_canvas) for module in modules]
    try:
        for module in modules:
            module.identity_canvas = identity_canvas
        yield
    finally:
        for module, original in saved:
            module.identity_canvas = original


def annotate(data, placement, scope, source, identity):
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(identity)) as image:
        original_size = ImageOps.exif_transpose(image).size
    target = identity_canvas(*original_size)
    result = io.BytesIO(data)
    with zipfile.ZipFile(result, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('identity-detail.json', json.dumps({
            'placement': placement, 'scope': scope,
            'original_identity_dimensions': original_size,
            'corrected_conditioning_dimensions': target,
            'original_identity_sha256': hashlib.sha256(identity).hexdigest(),
            'source_sha256': hashlib.sha256(source).hexdigest(),
            'policy': 'Resize original pixels directly. Integer multiple of legacy canvas preserves native Qwen aspect/token geometry; at most1024x1024 pixels. Low-detail inputs retain the legacy path. No nearest-neighbor fabrication of added detail.',
            'source_sha256_by_file': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                     for name in ('identity_detail.py', 'detail_reference_alignment.py')},
            'limits': 'Preserves input information; does not itself establish likeness, motion quality or native model capability.'
        }, indent=2))
    return result.getvalue()


def refine(source, identity):
    with detail_policy('qwen'):
        data = qwen.run_reference_alignment(source, identity, output_directory='/tmp/detail-qwen')
    return annotate(data, 'qwen', 'Qwen refinement of an already retained Klein frame', source, identity)


def cascade(source, identity, placement='both'):
    with detail_policy(placement):
        data = frozen_cascade(source, identity)
    return annotate(data, placement, 'Fresh two-editor reference preparation', source, identity)
