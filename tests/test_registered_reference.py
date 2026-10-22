import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registered_reference import similarity


class RegistrationTests(unittest.TestCase):
    def test_recovers_body_framing_without_mirror_or_face_squeeze(self):
        points = np.array([[1., 1.], [3., 1.], [1.3, 4.], [2.7, 4.]])
        angle = .12
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        destination = points @ rotation.T * .35 + [100., 120.]
        matrix = similarity(points, destination)
        actual = (matrix @ np.column_stack([points, np.ones(4)]).T).T[:, :2]
        self.assertTrue(np.allclose(actual, destination))
        singular = np.linalg.svd(matrix[:2, :2], compute_uv=False)
        self.assertTrue(np.allclose(singular, [.35, .35]))
        self.assertGreater(np.linalg.det(matrix[:2, :2]), 0)
