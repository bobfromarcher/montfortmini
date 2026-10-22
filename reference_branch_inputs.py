"""Frozen-input reference-branch diagnostic and transparent conditioning receipt."""
from pathlib import Path
import hashlib
import json
import numpy as np


def frozen_arrays(path):
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k].copy() for k in ('source', 'mask', 'reference')}
    source, mask, ref = (arrays[k] for k in ('source','mask','reference'))
    if source.shape != (17,272,480,3) or mask.shape != (17,272,480) or ref.shape != (272,480,3):
        raise ValueError('Unexpected frozen diagnostic dimensions')
    if any(a.dtype != np.float32 or not np.isfinite(a).all() or np.any((a<0)|(a>1)) for a in arrays.values()):
        raise ValueError('Expected finite float32 arrays in0..1')
    return arrays


class OpenJutsuFrozenBranchInputs:
    @classmethod
    def INPUT_TYPES(cls): return {'required': {}}
    RETURN_TYPES=('IMAGE','MASK','IMAGE')
    FUNCTION='load'
    CATEGORY='OpenJutsu/experimental'

    def load(self):
        import torch
        root=Path('/tmp/openjutsu-fixture')
        arrays=frozen_arrays(root/'conditioning.npz')
        np.savez_compressed(root/'runtime-conditioning.npz', **arrays)
        return (torch.from_numpy(arrays['source']), torch.from_numpy(arrays['mask']),
                torch.from_numpy(arrays['reference'])[None])


def receipt_arrays(positive, negative, latent, trim_latent):
    def array(value):
        # Float32 snapshots preserve fp16/bfloat16 values; record native dtypes
        # separately. Never change or replace objects returned to the sampler.
        if hasattr(value,'detach'): return value.detach().float().cpu().numpy()
        return np.asarray(value,dtype=np.float32)
    frames=positive[0][1]['vace_frames'][0]
    mask=positive[0][1]['vace_mask'][0]
    if trim_latent != 1 or frames.shape[2] != 6:
        raise ValueError('Expected one reference plus five control latent frames')
    arrays=dict(positive_text=array(positive[0][0]),negative_text=array(negative[0][0]),
                reference_prefix=array(frames[:,:,:trim_latent]),
                control_tail=array(frames[:,:,trim_latent:]),vace_mask=array(mask),
                initial_latent=array(latent['samples']))
    # Check both polarities actually receive the same VACE data.
    if not np.array_equal(array(negative[0][1]['vace_frames'][0]),array(frames)):
        raise ValueError('Negative VACE conditioning differs')
    if not np.array_equal(array(negative[0][1]['vace_mask'][0]),array(mask)):
        raise ValueError('Negative VACE mask differs')
    return arrays


class OpenJutsuConditioningReceipt:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'positive':('CONDITIONING',),'negative':('CONDITIONING',),
                             'latent':('LATENT',),'trim_latent':('INT',),'seed':('INT',)}}
    RETURN_TYPES=('CONDITIONING','CONDITIONING','LATENT')
    FUNCTION='record'
    CATEGORY='OpenJutsu/experimental'

    def record(self, positive, negative, latent, trim_latent, seed):
        root=Path('/tmp/openjutsu-fixture')
        arrays=receipt_arrays(positive,negative,latent,trim_latent)
        np.savez_compressed(root/'wan-conditioning.npz',**arrays)
        native=dict(positive_text=str(positive[0][0].dtype),negative_text=str(negative[0][0].dtype),
                    vace_frames=str(positive[0][1]['vace_frames'][0].dtype),
                    vace_mask=str(positive[0][1]['vace_mask'][0].dtype),initial_latent=str(latent['samples'].dtype))
        record=dict(normalization='Float32 CPU snapshots; no sampler input modification',
                    native_dtypes=native,trim_latent=trim_latent,sampler_seed=seed,
                    tensors={k:dict(shape=list(a.shape),sha256=hashlib.sha256(a.tobytes()).hexdigest()) for k,a in arrays.items()},
                    limits='Seed and latent shape/values recorded; actual generated sampler noise is not separately captured.')
        (root/'wan-conditioning.json').write_text(json.dumps(record,indent=2))
        return positive,negative,latent


NODE_CLASS_MAPPINGS={'OpenJutsuFrozenBranchInputs':OpenJutsuFrozenBranchInputs,
                     'OpenJutsuConditioningReceipt':OpenJutsuConditioningReceipt}
