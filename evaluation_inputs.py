"""Evaluation-only interventions. Never imported by the production graph."""
from pathlib import Path
import json

class OpenJutsuEvaluationInputs:
    @classmethod
    def INPUT_TYPES(cls): return {"required":{}}
    RETURN_TYPES=("IMAGE","MASK","IMAGE")
    FUNCTION="load"
    CATEGORY="montfortmini/evaluation"
    def load(self):
        import torch,numpy as np
        from PIL import Image
        root=Path('/tmp/openjutsu-fixture')
        settings=json.loads((root/'settings.json').read_text())
        n=settings['frames']
        source=np.stack([np.asarray(Image.open(root/'source'/f'{i:04d}.png').convert('RGB'),dtype=np.float32)/255 for i in range(n)])
        mask=np.stack([np.asarray(Image.open(root/'masks'/f'{i:04d}.png').convert('L'),dtype=np.float32)/255 for i in range(n)])
        reference=np.asarray(Image.open(root/'reference.png').convert('RGB'),dtype=np.float32)/255
        variant=settings.get('evaluation_variant','baseline')
        if settings['mode']=='object-swap' and variant!='source-retained':
            source=source*(1-mask[...,None])+.5*mask[...,None]
        if variant=='frozen-motion': source=np.repeat(source[:1],n,axis=0)
        if variant=='neutral-reference': reference=np.full_like(reference,.5)
        return torch.from_numpy(source),torch.from_numpy(mask),torch.from_numpy(reference)[None]

NODE_CLASS_MAPPINGS={"OpenJutsuEvaluationInputs":OpenJutsuEvaluationInputs}
