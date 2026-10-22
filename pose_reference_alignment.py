"""Native Qwen keypoint+identity reference preparation; no source-person RGB required."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from detail_reference_alignment import detail_policy
import qwen_reference_alignment

PROMPT = (
    'Render exactly one character from image 2 in the body pose shown in image 1. '
    'Image 1 supplies only body posture, joint positions, head direction, scale and framing; '
    'it may be a photograph or a colored skeleton keypoint map. '
    'Image 2 is the sole source of character appearance: preserve the face, hairstyle, beard, '
    'eyeglasses or other accessories, every clothing item, garment colors and materials. '
    'Do not copy the source performer\'s face, hair, headwear or clothing from image 1. '
    'Keep the shoulders, elbows, wrists, hips and knees at the positions shown in image 1. '
    'Keep the hands in those positions and turn the head in the shown direction. '
    'Use the visual rendering style of image 2 with plausible anatomy, on a plain neutral '
    'studio background. No text, extra subject, unrelated props or extra limbs.'
)


def run_reference_alignment(source, identity, guide):
    """Root original hashes retain the RGB source provenance; stage source is guide."""
    with detail_policy('qwen'):
        data = qwen_reference_alignment.run_reference_alignment(
            guide, identity, prompt=PROMPT, output_directory='/tmp/pose-reference-stage')
    result = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as stage, zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED) as out:
        manifest = json.loads(stage.read('manifest.json'))
        for entry in stage.infolist():
            if not entry.is_dir():
                out.writestr('qwen/' + entry.filename, stage.read(entry))
        if manifest['status'] == 'succeeded':
            out.writestr('anchor.png', stage.read('anchor.png'))
        out.writestr('original-source.png', source)
        out.writestr('manifest.json', json.dumps({
            'status': manifest['status'], 'failure': manifest['failure'],
            'original_source_sha256': hashlib.sha256(source).hexdigest(),
            'original_identity_sha256': hashlib.sha256(identity).hexdigest(),
            'guide_sha256': hashlib.sha256(guide).hexdigest(), 'stages': [manifest],
            'candidate': 'Qwen2511 native pose guide + original identity detail; no Klein',
            'software_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                               for name in ('pose_reference_alignment.py', 'identity_detail.py',
                                            'detail_reference_alignment.py')},
            'limitations': ['Estimated2D pose omits detailed fingers and exact3D head orientation.',
                           'Plain generated background; no source-background preservation claim.',
                           'Reference-only evidence cannot establish motion/video quality.']}, indent=2))
    return result.getvalue()
