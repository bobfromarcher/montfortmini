import unittest
import numpy as np
from object_reference_luma_inputs import reference_luma_control
from object_luminance_inputs import luminance_control


class ReferenceLumaTests(unittest.TestCase):
    def test_target_only_fixed_gain_keeps_background_motion_and_relative_shading(self):
        source=np.full((2,24,32,3),.8,dtype=np.float32)
        edit=np.zeros((2,24,32),dtype=np.float32);edit[:,2:22,2:30]=1
        fg=np.zeros_like(edit)
        for i in range(2):
            fg[i,7:17,7+i:17+i]=1
            source[i,7:17,7+i:17+i]=[.9,.6,.1]
            source[i,12:17,7+i:17+i]*=.6
        reference=np.full((24,32,3),.2,dtype=np.float32);ref_mask=np.ones((24,32),bool)
        result,info=reference_luma_control(source,edit,reference,fg,ref_mask)
        baseline=luminance_control(source,edit)
        self.assertTrue(np.array_equal(result[edit==0],source[edit==0]))
        self.assertTrue(np.array_equal(result[:,3:5,25:27],baseline[:,3:5,25:27]))
        self.assertTrue(np.array_equal(result[...,0][edit==1],result[...,1][edit==1]))
        self.assertTrue(np.array_equal(result[0,10,11],result[1,10,12]))
        self.assertAlmostEqual(float(result[0,10,11,0]/baseline[0,10,11,0]),info['gain'],places=6)
        self.assertAlmostEqual(float(result[0,14,11,0]/result[0,10,11,0]),.6,places=6)

    def test_rejects_foreground_leaking_outside_edit_region(self):
        with self.assertRaises(ValueError):
            reference_luma_control(np.ones((1,4,4,3)),np.zeros((1,4,4)),np.ones((4,4,3)),np.ones((1,4,4)),np.ones((4,4),bool))
