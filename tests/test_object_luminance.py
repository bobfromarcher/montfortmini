import unittest
import numpy as np
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
