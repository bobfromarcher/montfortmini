"""Read only frozen CPU controls; source RGB is not body-pose conditioning."""
class OpenJutsuExplicitInputs:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{}}
    RETURN_TYPES=('IMAGE','MASK','IMAGE','IMAGE','IMAGE')
    FUNCTION='load'
    CATEGORY='montfortmini/validation'
    def load(self):
        import numpy as np
        import torch
        with np.load('/tmp/openjutsu-fixture/conditioning.npz',allow_pickle=False) as data:
            return tuple(torch.from_numpy(data[k].copy())[None] if k=='reference'
                         else torch.from_numpy(data[k].copy())
                         for k in ('source','mask','reference','pose','face'))
NODE_CLASS_MAPPINGS={'OpenJutsuExplicitInputs':OpenJutsuExplicitInputs}
