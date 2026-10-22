import unittest
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from PIL import Image
import object_luminance_inputs as candidate
from object_luminance_inputs import luminance_control


class LuminanceControlTests(unittest.TestCase):
    def test_preserves_motion_geometry_and_background_without_target_chroma(self):
        # A differently placed two-tone object on each frame must keep its
        # silhouette and shading, while outside context stays bit-exact.
        source=np.full((2,5,7,3),.8,dtype=np.float32)
        mask=np.zeros((2,5,7),dtype=np.float32)
        for i in range(2):
            source[i,1:4,1+i:3+i]=[1,.7,.05]
            source[i,2:4,1+i:3+i]=[.5,.3,.02]
            mask[i,1:4,1+i:3+i]=1
        result=luminance_control(source,mask)
        self.assertTrue(np.array_equal(result[mask==0],source[mask==0]))
        self.assertTrue(np.array_equal(result[...,0][mask==1],result[...,1][mask==1]))
        self.assertTrue(np.array_equal(result[...,1][mask==1],result[...,2][mask==1]))
        self.assertGreater(result[0,1,1,0],result[0,2,1,0])
        self.assertEqual(result[0,1,1,0],result[1,1,2,0])

    def test_rejects_soft_masks_for_this_binary_diagnostic(self):
        with self.assertRaises(ValueError):luminance_control(np.ones((1,2,2,3)),np.full((1,2,2),.5))

    def test_executed_node_saves_the_exact_returned_conditioning(self):
        class Tensor:
            def __init__(self,array):self.array=array
            def numpy(self):return self.array
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'source').mkdir()
            (root/'settings.json').write_text(json.dumps({'mode':'object-swap','frames':2}))
            source=np.zeros((2,3,4,3),dtype=np.uint8);source[:]=[240,170,20]
            for i in range(2):Image.fromarray(source[i]).save(root/'source'/f'{i:04d}.png')
            masks=np.zeros((2,3,4),dtype=np.float32);masks[:,:,1:3]=1
            reference=np.full((1,3,4,3),.25,dtype=np.float32)
            with patch.dict('sys.modules',{'torch':SimpleNamespace(from_numpy=Tensor)}), \
                 patch.object(candidate,'Path',return_value=root), \
                 patch('media_pipeline.OpenJutsuMediaInputs.load',return_value=(None,Tensor(masks),Tensor(reference))):
                control,returned_mask,returned_reference=candidate.OpenJutsuLuminanceInputs().load()
            with np.load(root/'runtime-conditioning.npz') as saved:
                self.assertTrue(np.array_equal(saved['source'],control.numpy()))
                self.assertTrue(np.array_equal(saved['mask'],returned_mask.numpy()))
                self.assertTrue(np.array_equal(saved['reference'],returned_reference.numpy()[0]))
            self.assertTrue(np.array_equal(control.numpy(),luminance_control(source.astype(np.float32)/255,masks)))
