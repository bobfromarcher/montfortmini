"""Unvalidated shape-control candidate; never selected by the production graph.

The original neutral fill deletes all target geometry. This candidate retains
source luminance inside the edit region while discarding its RGB chroma.
Only a future paired video experiment can establish whether this helps.
"""
from pathlib import Path
import json


def luminance_control(source,mask):
    """RGB float arrays in0..1; preserve outside pixels and inside luminance.

Rec.709 coefficients applied to encoded RGB are a luma proxy, not calibrated
linear-light luminance. No color is copied into the reactive edit branch.
"""
    import numpy as np
    source=np.asarray(source,dtype=np.float32);mask=np.asarray(mask,dtype=np.float32)
    if source.shape[:-1]!=mask.shape or source.shape[-1]!=3:
        raise ValueError('Expected matching THW3 RGB and THW masks')
    if not np.isfinite(source).all() or not np.isfinite(mask).all():raise ValueError('Nonfinite input')
    if np.any((mask!=0)&(mask!=1)):raise ValueError('This diagnostic requires binary masks')
    gray=(source*np.asarray([.2126,.7152,.0722],dtype=np.float32)).sum(axis=-1,keepdims=True)
    return np.where(mask[...,None]>0,gray,source)


class OpenJutsuLuminanceInputs:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{}}
    RETURN_TYPES=('IMAGE','MASK','IMAGE')
    FUNCTION='load'
    CATEGORY='OpenJutsu/experimental'

    def load(self):
        import numpy as np
        import torch
        from PIL import Image
        from media_pipeline import OpenJutsuMediaInputs
        root=Path('/tmp/openjutsu-fixture')
        settings=json.loads((root/'settings.json').read_text())
        if settings['mode']!='object-swap':raise ValueError('Object-only diagnostic')
        _,mask,reference=OpenJutsuMediaInputs().load()
        source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(settings['frames'])])
        control=luminance_control(source,mask.numpy())
        # Retain the exact tensors returned by the executed Comfy node, rather
        # than relying only on a matching offline preparation script.
        np.savez_compressed(root/'runtime-conditioning.npz',source=control,
                            mask=mask.numpy(),reference=reference.numpy()[0])
        return torch.from_numpy(control),mask,reference


NODE_CLASS_MAPPINGS={'OpenJutsuLuminanceInputs':OpenJutsuLuminanceInputs}
