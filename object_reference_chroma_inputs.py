"""Research-only reference chromaticity control; explicit foreground masks required.

Single-factor contrast against reference_luma_control. No generated pixels are
used. Encoded RGB luma is held fixed; this is not physical relighting.
"""
from pathlib import Path
import json
import numpy as np
from object_reference_luma_inputs import reference_luma_control


def reference_chroma_control(source, edit_masks, reference, foreground, reference_foreground):
    base, record = reference_luma_control(source, edit_masks, reference, foreground, reference_foreground)
    reference = np.asarray(reference, dtype=np.float32)
    if not np.isfinite(reference).all() or np.any((reference < 0) | (reference > 1)):
        raise ValueError('Reference must be finite RGB in 0..1')
    coefficients = np.asarray([.2126, .7152, .0722], dtype=np.float32)
    rgb = np.median(reference[np.asarray(reference_foreground, dtype=bool)], axis=0)
    luma = float(rgb @ coefficients)
    if luma <= 0:
        raise ValueError('Zero reference foreground chromaticity')
    ratios = rgb / np.float32(luma)
    # Match the existing fixed spatial feather, leaving brightness unchanged.
    positions = np.arange(-2, 3, dtype=np.float64)
    kernel = np.exp(-.5 * positions**2)
    kernel = (kernel / kernel.sum()).astype(np.float32)
    fg = np.asarray(foreground, dtype=np.float32)
    padded = np.pad(fg, ((0, 0), (0, 0), (2, 2)), mode='reflect')
    horizontal = sum(kernel[i] * padded[:, :, i:i+fg.shape[2]] for i in range(5))
    padded = np.pad(horizontal, ((0, 0), (2, 2), (0, 0)), mode='reflect')
    alpha = sum(kernel[i] * padded[:, i:i+fg.shape[1], :] for i in range(5)) * edit_masks
    colored = base * (1 + alpha[..., None] * (ratios - 1))
    active = alpha > 0
    if np.any((colored[active] < 0) | (colored[active] > 1)):
        raise ValueError('Chromaticity would clip; single-factor luma contrast invalid')
    result = np.where(active[..., None], colored, base)
    delta = float(np.max(np.abs((result * coefficients).sum(-1) - (base * coefficients).sum(-1))))
    if delta > 2e-7:
        raise ValueError('Encoded luma changed beyond float32 tolerance')
    record.update(reference_median_rgb=rgb.tolist(), reference_rgb_per_unit_luma=ratios.tolist(),
                  luma_delta_vs_prior_max=delta, clipped_values=0,
                  method='Existing reference-luma control plus one fixed reference-median RGB/luma ratio, same 5x5 sigma1 foreground feather. Original source geometry, relative shading and luma retained; no generated pixels.',
                  limits='Encoded RGB chromaticity is not reflectance or physical relighting. Explicit foreground annotations required; fixture oracle is not generic segmentation.')
    return result, record


class OpenJutsuReferenceChromaInputs:
    @classmethod
    def INPUT_TYPES(cls): return {'required': {}}
    RETURN_TYPES = ('IMAGE', 'MASK', 'IMAGE')
    FUNCTION = 'load'
    CATEGORY = 'OpenJutsu/experimental'

    def load(self):
        import torch
        from PIL import Image
        from media_pipeline import OpenJutsuMediaInputs
        root = Path('/tmp/openjutsu-fixture')
        settings = json.loads((root/'settings.json').read_text())
        if settings['mode'] != 'object-swap': raise ValueError('Object-only diagnostic')
        _, mask, reference = OpenJutsuMediaInputs().load()
        def read(path, mode): return np.asarray(Image.open(path).convert(mode), dtype=np.float32)/255
        source = np.stack([read(root/'source'/f'{i:04d}.png', 'RGB') for i in range(settings['frames'])])
        fg = np.stack([read(root/'foreground'/f'{i:04d}.png', 'L') for i in range(settings['frames'])])
        control, record = reference_chroma_control(source, mask.numpy(), reference.numpy()[0], fg,
                                                  read(root/'reference-foreground.png', 'L') > 0)
        np.savez_compressed(root/'runtime-conditioning.npz', source=control, mask=mask.numpy(), reference=reference.numpy()[0])
        (root/'runtime-chroma-normalization.json').write_text(json.dumps(record, indent=2))
        return torch.from_numpy(control), mask, reference


NODE_CLASS_MAPPINGS = {'OpenJutsuReferenceChromaInputs': OpenJutsuReferenceChromaInputs}
