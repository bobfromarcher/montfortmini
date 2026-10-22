"""Experimental foreground-only reference-luma control; no production selection.

Foreground annotations are explicit inputs. Fixture-specific color extraction
in the study preparer is an oracle, not generic object segmentation.
"""
from pathlib import Path
import json

import numpy as np
from object_luminance_inputs import luminance_control


def reference_luma_control(source,edit_masks,reference,foreground,reference_foreground):
    source=np.asarray(source,dtype=np.float32);reference=np.asarray(reference,dtype=np.float32)
    edit_masks=np.asarray(edit_masks,dtype=np.float32)
    foreground=np.asarray(foreground,dtype=np.float32)
    reference_foreground=np.asarray(reference_foreground,dtype=bool)
    if foreground.shape!=edit_masks.shape or reference_foreground.shape!=reference.shape[:2]:
        raise ValueError('Foreground annotation shape mismatch')
    if np.any((foreground!=0)&(foreground!=1)) or np.any(foreground>edit_masks):
        raise ValueError('Binary foreground must stay inside the edit region')
    if not reference_foreground.any() or any(not m.any() for m in foreground):
        raise ValueError('Missing foreground annotation')
    control=luminance_control(source,edit_masks)
    coefficients=np.asarray([.2126,.7152,.0722],dtype=np.float32)
    source_luma=(source*coefficients).sum(axis=-1)
    ref_luma=(reference*coefficients).sum(axis=-1)
    # A single gain from the first source frame avoids framewise gain pumping.
    source_median=float(np.median(source_luma[0][foreground[0]>0]))
    reference_median=float(np.median(ref_luma[reference_foreground]))
    if source_median<=0:raise ValueError('Zero source foreground luma')
    gain=reference_median/source_median
    if not .25<=gain<=2:raise ValueError('Gain outside preregistered diagnostic range')
    # NumPy-only separable5x5 sigma1 Gaussian, reflect101 boundaries. Avoid a
    # segmentation-library dependency in the inference container.
    positions=np.arange(-2,3,dtype=np.float64)
    kernel=np.exp(-.5*positions**2);kernel=(kernel/kernel.sum()).astype(np.float32)
    padded=np.pad(foreground,((0,0),(0,0),(2,2)),mode='reflect')
    horizontal=sum(kernel[i]*padded[:,:,i:i+foreground.shape[2]] for i in range(5))
    padded=np.pad(horizontal,((0,0),(2,2),(0,0)),mode='reflect')
    alpha=sum(kernel[i]*padded[:,i:i+foreground.shape[1],:] for i in range(5))*edit_masks
    factor=(1+alpha*np.float32(gain-1))[...,None]
    # Explicit selection preserves all pixels where alpha is zero bit-for-bit.
    result=np.where(alpha[...,None]>0,np.clip(control*factor,0,1),control)
    return result,{'gain':gain,'source_first_frame_median_luma':source_median,
                   'reference_median_luma':reference_median,'feather_kernel':5,'feather_sigma':1.0,
                   'method':'One fixed reference/source foreground encoded-RGB-luma gain;5x5 sigma1 feather inside the original edit mask. Source geometry and relative shading retained. No generated pixels consulted.',
                   'limits':'Encoded RGB is not linear-light luminance or calibrated reflectance. Foreground annotations are required; their automatic estimation is not validated.'}


class OpenJutsuReferenceLumaInputs:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{}}
    RETURN_TYPES=('IMAGE','MASK','IMAGE')
    FUNCTION='load'
    CATEGORY='OpenJutsu/experimental'

    def load(self):
        import torch
        from PIL import Image
        from media_pipeline import OpenJutsuMediaInputs
        root=Path('/tmp/openjutsu-fixture');settings=json.loads((root/'settings.json').read_text())
        if settings['mode']!='object-swap':raise ValueError('Object-only diagnostic')
        _,mask,reference=OpenJutsuMediaInputs().load()
        source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(settings['frames'])])
        foreground=np.stack([np.asarray(Image.open(root/'foreground'/f'{i:04d}.png').convert('L'),dtype=np.float32)/255 for i in range(settings['frames'])])
        ref_mask=np.asarray(Image.open(root/'reference-foreground.png').convert('L'))>0
        control,record=reference_luma_control(source,mask.numpy(),reference.numpy()[0],foreground,ref_mask)
        np.savez_compressed(root/'runtime-conditioning.npz',source=control,mask=mask.numpy(),reference=reference.numpy()[0])
        (root/'runtime-luma-normalization.json').write_text(json.dumps(record,indent=2))
        return torch.from_numpy(control),mask,reference


NODE_CLASS_MAPPINGS={'OpenJutsuReferenceLumaInputs':OpenJutsuReferenceLumaInputs}
