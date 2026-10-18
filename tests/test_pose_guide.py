import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pose_guide import to_openpose, draw_pose


class PoseGuideTests(unittest.TestCase):
    def test_joint_convention_preserves_anatomical_sides(self):
        # Detector x is camera-space; never reverse left/right with a mirror heuristic.
        points = [{'x': i / 40, 'y': .4, 'visibility': .9} for i in range(33)]
        mapped = to_openpose(points)
        self.assertEqual(mapped[4], points[16])  # OpenPose right wrist
        self.assertEqual(mapped[7], points[15])  # OpenPose left wrist
        self.assertAlmostEqual(mapped[1]['x'], (points[11]['x'] + points[12]['x']) / 2)

    def test_invisible_or_out_of_frame_body_is_not_invented(self):
        joints = [{'x': 2, 'y': 2, 'visibility': 1} for _ in range(18)]
        joints[0] = {'x': .5, 'y': .5, 'visibility': .2}
        image = draw_pose(joints, (650, 750))
        self.assertEqual(image.size, (650, 750))
        self.assertFalse(np.asarray(image).any())
