"""Native motion in the optional Linux GPU Docker image, without cloud calls."""
import base64
import io
import json
from pathlib import Path
import shutil
import sys
import zipfile


def generate(data):
    if data.get('mode') != 'motion-transfer':
        from legacy_local_inference import generate as object_generate
        return object_generate(data)
    if sys.platform != 'linux':
        raise RuntimeError('Use the documented Linux GPU container for native local inference')
    from native_motion_backend import prepare, render
    # Cloud control workers are single-use. The local server reuses its process.
    # This fixed internal directory contains only the previous job's controls.
    controls_root = Path('/tmp/upstream-input')
    if controls_root.resolve() != Path('/tmp/upstream-input'):
        raise ValueError('Unexpected controls directory target')
    if controls_root.exists():
        shutil.rmtree(controls_root)
    prepared = prepare.local(data)
    bundle = render.local(prepared['inputs'], prepared['graph'])
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        if json.loads(archive.read('candidate.json'))['status'] != 'succeeded':
            raise RuntimeError('Native local render failed; no retry')
        return {
            'source_video_b64':base64.b64encode(archive.read('source.mp4')).decode(),
            'generated_video_b64':base64.b64encode(archive.read('generated.mp4')).decode(),
            'composite_video_b64':base64.b64encode(archive.read('composite.mp4')).decode(),
            'manifest':json.loads(archive.read('manifest.json')),
            'workflow':json.loads(archive.read('workflow-api.json')),
        }
