import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evaluation'))
from object_color_diagnostics import pixel_stats,summarize


class ColorDiagnosticsTests(unittest.TestCase):
    def test_fixed_roi_includes_wrong_color_instead_of_dropping_it(self):
        rgb=np.full((6,6,3),[255,255,0],dtype=np.uint8)
        region=np.zeros((6,6),bool);region[1:5,1:5]=True
        reference=np.array([.1,.7,.2])
        row=pixel_stats(rgb,region,reference)
        self.assertEqual(row['pixels'],16)
        self.assertEqual(row['median_rgb_255'],[255,255,0])
        self.assertGreater(row['chromaticity_distance'],.1)
        rgb[~region]=[0,0,255]
        self.assertEqual(pixel_stats(rgb,region,reference),row)

    def test_brightness_and_chromaticity_are_separate_and_temporal_change_retained(self):
        region=np.ones((6,6),bool);ref=np.array([.1,.7,.2])
        a=pixel_stats(np.full((6,6,3),[10,70,20],dtype=np.uint8),region,ref)
        b=pixel_stats(np.full((6,6,3),[20,140,40],dtype=np.uint8),region,ref)
        self.assertAlmostEqual(a['chromaticity_distance'],0)
        self.assertAlmostEqual(b['chromaticity_distance'],0)
        self.assertGreater(b['encoded_luma_p10_median_p90'][1],a['encoded_luma_p10_median_p90'][1])
        self.assertGreater(summarize([a,b])['max_adjacent_rgb_step_255'],0)
