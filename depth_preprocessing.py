"""Pinned Apache2 CPU depth guide; generator weights are unchanged."""
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile

REPO = 'depth-anything/Depth-Anything-V2-Small-hf'
REVISION = '5426e4f0f36572d16453bbda7a8389317b1bef99'
WEIGHT_SHA = '3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70'
MODEL = Path('/opt/depth-model')


def download():
    from huggingface_hub import hf_hub_download
    for name in ('config.json', 'preprocessor_config.json', 'model.safetensors'):
        hf_hub_download(REPO, name, revision=REVISION, local_dir=MODEL, token=False)
    if hashlib.sha256((MODEL / 'model.safetensors').read_bytes()).hexdigest() != WEIGHT_SHA:
        raise RuntimeError('Depth model digest mismatch')


def prepare(source, pose):
    import numpy as np
    from PIL import Image, ImageOps
    import torch
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    start = time.monotonic()
    torch.set_num_threads(2)
    with Image.open(io.BytesIO(source)) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
    processor = AutoImageProcessor.from_pretrained(MODEL, local_files_only=True)
    model = AutoModelForDepthEstimation.from_pretrained(MODEL, local_files_only=True, use_safetensors=True).to('cpu').eval()
    inputs = processor(images=image, return_tensors='pt')
    with torch.inference_mode():
        prediction = model(**inputs).predicted_depth
        depth = torch.nn.functional.interpolate(prediction.unsqueeze(1), size=(image.height, image.width),
                                                mode='bicubic', align_corners=False)[0, 0].cpu().numpy()
    low, high = np.percentile(depth, [1, 99])
    if not np.isfinite(depth).all() or high <= low:
        raise RuntimeError('Invalid depth guide; no GPU inference')
    normalized = np.clip((depth - low) / (high - low), 0, 1)
    rendered = Image.fromarray(np.rint(normalized * 255).astype('uint8')).convert('RGB')
    png = io.BytesIO(); rendered.save(png, format='PNG')
    raw = io.BytesIO(); np.save(raw, depth, allow_pickle=False)
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('source.png', source); z.writestr('pose.png', pose)
        z.writestr('depth.png', png.getvalue()); z.writestr('depth.npy', raw.getvalue())
        z.writestr('provenance.json', json.dumps({
            'repo': REPO, 'revision': REVISION, 'license': 'Apache-2.0', 'device': 'CPU',
            'weight_sha256': WEIGHT_SHA, 'source_sha256': hashlib.sha256(source).hexdigest(),
            'pose_sha256': hashlib.sha256(pose).hexdigest(),
            'depth_sha256': hashlib.sha256(png.getvalue()).hexdigest(),
            'source_dimensions': list(image.size), 'normalization_percentiles': [1, 99],
            'normalization_values': [float(low), float(high)], 'elapsed_seconds': time.monotonic() - start,
            'torch': torch.__version__,
            'limits': 'Estimated relative inverse depth, brighter near. Not metric depth, true surface normals, identity or annotated orientation. Source headwear shape may remain in geometry.'}, indent=2))
    return result.getvalue()


if __name__ == '__main__':
    download()
