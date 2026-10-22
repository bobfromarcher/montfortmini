"""Exploratory third-input orientation guide; all earlier candidates remain frozen."""
from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import zipfile
import identity_first_alignment as first
import pose_reference_alignment as pose
import qwen_reference_alignment as qwen
import sdk_runner


@contextmanager
def depth_policy():
    builder, prompt, sdk = qwen.build_graph, pose.PROMPT, sdk_runner.run_with_sdk
    def build(*args, **kwargs):
        graph = builder(*args, **kwargs)
        graph['18'] = {'class_type': 'LoadImage', 'inputs': {'image': 'identity-body-depth.png'}}
        for key in ('6', '7'):
            graph[key]['inputs']['image3'] = ['18', 0]
        return graph
    try:
        qwen.build_graph = build
        # A third reference adds attention work. Keep the existing660s worker cap,
        # with a bounded600s wait for the same submitted job, never a resubmission.
        def wait_for_same_job(*args, **kwargs):
            kwargs['timeout'] = 600
            return sdk(*args, **kwargs)
        sdk_runner.run_with_sdk = wait_for_same_job
        pose.PROMPT += (' Image 3 is an estimated depth map of the source, brighter nearer the camera. '
                        'Use it only for three-dimensional body orientation and limb placement, '
                        'including which side of the torso faces the camera. '
                        'Preserve the character appearance and clothes from the appearance reference. '
                        'Do not copy the source performer\'s headwear or clothing from the depth silhouette.')
        yield
    finally:
        qwen.build_graph, pose.PROMPT = builder, prompt
        sdk_runner.run_with_sdk = sdk


def run_reference_alignment(source, identity, bundle):
    import numpy as np
    from PIL import Image, ImageOps
    with zipfile.ZipFile(io.BytesIO(bundle)) as z:
        depth, guide, cpu_source = (z.read(name) for name in ('depth.png', 'pose.png', 'source.png'))
        provenance = json.loads(z.read('provenance.json'))
    def rgb(data):
        with Image.open(io.BytesIO(data)) as im:
            return np.asarray(ImageOps.exif_transpose(im).convert('RGB'), dtype='int16')
    a, b = rgb(source), rgb(cpu_source)
    if a.shape != b.shape or np.abs(a-b).mean() > 1:
        raise ValueError('Depth guide is from another source frame')
    if hashlib.sha256(depth).hexdigest() != provenance['depth_sha256']:
        raise ValueError('Depth guide digest changed')
    with Image.open(io.BytesIO(depth)) as im:
        depth_image = ImageOps.exif_transpose(im).convert('RGB').resize(qwen.source_canvas(a.shape[1], a.shape[0]), Image.Resampling.LANCZOS)
    path = Path('/opt/ComfyUI/input/identity-body-depth.png')
    path.parent.mkdir(parents=True, exist_ok=True); depth_image.save(path)
    with depth_policy():
        data = first.run_reference_alignment(source, identity, guide)
    stream = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as new:
        for entry in old.infolist():
            value = old.read(entry)
            if entry.filename == 'manifest.json':
                record = json.loads(value)
                record['candidate'] = 'Identity-first Qwen2511 + estimated depth as image3 (exploratory protocol amendment)'
                record['depth_provenance'] = provenance
                record['software_sha256']['depth_identity_alignment.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
                value = json.dumps(record, indent=2).encode()
            new.writestr(entry.filename, value)
        new.writestr('depth-original.png', depth)
        new.writestr('qwen/depth-conditioning.png', path.read_bytes())
        new.writestr('depth-provenance.json', json.dumps(provenance, indent=2))
    return stream.getvalue()
