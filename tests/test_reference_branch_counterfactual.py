import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evaluation'))
from prepare_reference_branch import counterfactual_reference


class ReferenceCounterfactualTests(unittest.TestCase):
    def test_hue_changes_without_luma_background_or_shading_changes(self):
        ref=np.full((8,8,3),.8,np.float32);mask=np.zeros((8,8),bool);mask[2:6,2:6]=True
        ref[mask]=[.1,.5,.15];ref[4:6,2:6]*=.6
        changed,record=counterfactual_reference(ref,mask)
        coefficients=np.array([.2126,.7152,.0722],np.float32)
        np.testing.assert_allclose(changed@coefficients,ref@coefficients,rtol=0,atol=2e-7)
        np.testing.assert_array_equal(changed[~mask],ref[~mask])
        self.assertTrue(np.all(changed[mask,0]>changed[mask,1]))
        self.assertTrue(np.all(changed[mask,2]>changed[mask,1]))
        np.testing.assert_allclose(changed[4,3]/changed[3,3],.6,atol=1e-6)

    def test_rejects_clipping_instead_of_silently_changing_brightness(self):
        with self.assertRaisesRegex(ValueError,'clip'):
            counterfactual_reference(np.ones((4,4,3),np.float32),np.ones((4,4),bool))
