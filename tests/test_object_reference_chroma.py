import unittest
import numpy as np
from object_reference_chroma_inputs import reference_chroma_control
from object_reference_luma_inputs import reference_luma_control


class ReferenceChromaTests(unittest.TestCase):
    def fixture(self):
        source = np.full((2,24,32,3), .4, dtype=np.float32)
        edit = np.zeros((2,24,32), dtype=np.float32); edit[:,2:22,2:30] = 1
        fg = np.zeros_like(edit)
        for i in range(2):
            fg[i,7:17,7+i:17+i] = 1
            source[i,7:17,7+i:17+i] = [.9,.6,.1]
            source[i,12:17,7+i:17+i] *= .6
        ref = np.full((24,32,3), [.13,.55,.19], dtype=np.float32)
        return source, edit, ref, fg, np.ones((24,32),bool)

    def test_chroma_changes_without_luma_geometry_motion_or_background_change(self):
        args = self.fixture()
        result, record = reference_chroma_control(*args)
        prior, _ = reference_luma_control(*args)
        c = np.array([.2126,.7152,.0722],dtype=np.float32)
        np.testing.assert_allclose(result@c, prior@c, rtol=0, atol=2e-7)
        self.assertTrue(np.array_equal(result[args[1] == 0], args[0][args[1] == 0]))
        self.assertTrue(np.array_equal(result[0,10,11], result[1,10,12]))
        np.testing.assert_allclose(result[0,10,11]/result[0,10,11,1], args[2][0,0]/args[2][0,0,1], atol=1e-6)
        np.testing.assert_allclose(result[0,14,11]/result[0,10,11], .6, atol=1e-6)
        self.assertEqual(record['clipped_values'], 0)

    def test_rejects_reference_nan_and_clipping_instead_of_silent_luma_change(self):
        source, edit, ref, fg, rf = self.fixture()
        ref[0,0,0] = np.nan
        with self.assertRaises(ValueError): reference_chroma_control(source,edit,ref,fg,rf)
        source[0,9,9] = 1
        ref[:] = [0, .7, 0]
        with self.assertRaisesRegex(ValueError,'clip'):
            reference_chroma_control(source,edit,ref,fg,rf)
