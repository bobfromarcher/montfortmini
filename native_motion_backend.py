"""App motion path: CPU whole-body controls, native Comfy graph, official SDK.

Single-person footage and a complete character reference are the validated use.
No reference generation, retargeting, foreground segmentation or portrait completion.
"""
import hashlib
import io
import json
from pathlib import Path
import zipfile

import modal
import native_recipe_candidate as candidate
import upstream_motion_candidate as upstream
from native_recipe_models import ASSETS
from native_recipe_workflow import build_graph
from native_recipe_fixture import validate_fixture

HERE = Path(__file__).parent
app = modal.App('montfortmini-native-motion')
SOURCE_NAMES = tuple(dict.fromkeys((*candidate.NAMES, 'upstream_motion_candidate.py',
    'upstream_motion_controls.py', 'media_pipeline.py', 'native_motion_backend.py')))
control_image = upstream.cpu_base_image.apt_install('ffmpeg')
gpu_image = candidate.image
for name in SOURCE_NAMES:
    control_image = control_image.add_local_file(HERE / name, '/root/' + name)
    if name not in candidate.NAMES:
        gpu_image = gpu_image.add_local_file(HERE / name, '/root/' + name)
gpu_image = gpu_image.add_local_dir(HERE / 'vendor/wan_animate', '/root/vendor/wan_animate')


def archive_prepared(prepared):
    """Preserve prepared source/reference pixels and compositor mask PNGs."""
    import numpy as np
    from PIL import Image
    root = Path(prepared['root'])
    frames, width, height = (prepared[k] for k in ('frames', 'width', 'height'))
    source = np.stack([np.asarray(Image.open(root / 'source' / f'{i:04d}.png').convert('RGB'), dtype=np.float32) / 255
                       for i in range(frames)])
    masks = np.stack([np.asarray(Image.open(root / 'masks' / f'{i:04d}.png').convert('L'), dtype=np.float32) / 255
                      for i in range(frames)])
    reference = np.asarray(Image.open(root / 'reference.png').convert('RGB'), dtype=np.float32) / 255
    # Upstream replaces these placeholders with its pinned detector outputs.
    for folder, size in (('pose', (width, height)), ('face', (512, 512))):
        (root / folder).mkdir(exist_ok=True)
        for i in range(frames):
            Image.new('RGB', size).save(root / folder / f'{i:04d}.png')
    np.savez_compressed(root / 'conditioning.npz', source=source, mask=masks, reference=reference)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in ('source', 'masks', 'pose', 'face'):
            for i in range(frames):
                archive.write(root / folder / f'{i:04d}.png', f'{folder}/{i:04d}.png')
        for name in ('reference.png', 'settings.json', 'conditioning.npz'):
            archive.write(root / name, name)
    return out.getvalue()


@app.function(image=control_image, cpu=2, memory=16384, timeout=900,
              max_containers=1, min_containers=0, scaledown_window=2,
              retries=0, single_use_containers=True)
def prepare(data):
    from media_pipeline import prepare_media
    from upstream_motion_controls import prepare as controls
    prepared = prepare_media(data, native_motion=True)
    if prepared['mode'] != 'motion-transfer':
        raise ValueError('Native motion backend only accepts motion transfer')
    inputs = controls(archive_prepared(prepared))
    graph = build_graph(prepared['width'], prepared['height'], prepared['frames'])
    graph['9']['inputs']['seed'] = prepared['seed']
    if prepared['prompt']:
        graph['4']['inputs']['text'] = prepared['prompt']
    validate_fixture(inputs, frames=prepared['frames'], width=prepared['width'], height=prepared['height'])
    return {'inputs': inputs, 'graph': graph}


@app.function(image=gpu_image, gpu='L40S', cpu=2, memory=65536, timeout=900,
              startup_timeout=180, max_containers=1, min_containers=0,
              scaledown_window=2, retries=0, single_use_containers=True)
def render(inputs, graph):
    import modal_probe
    original = modal_probe.masked_replacement

    class Native:
        @staticmethod
        def local(graph, info, deadline, precision='auto'):
            info.update(repo=ASSETS[0]['repo'], revision=ASSETS[0]['revision'],
                        mode='motion-transfer', input_provenance='User-selected source video and complete character reference; pinned ViTPose133 CPU controls')
            return original.local(graph, info, deadline, precision)

    modal_probe.masked_replacement = Native()
    try:
        # Retains SDK output, graph, raw/composited PNGs and resource telemetry.
        result = candidate.render.local(inputs, graph)
    finally:
        modal_probe.masked_replacement = original
    stream = io.BytesIO(result)
    with zipfile.ZipFile(stream, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('service-runtime.json', json.dumps({
            'source_sha256': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in SOURCE_NAMES},
            'backend': 'native Wan2.2-Animate with Lightx2v and relighting adapters',
            'input_archive_sha256': hashlib.sha256(inputs).hexdigest()}, indent=2))
    return stream.getvalue()
