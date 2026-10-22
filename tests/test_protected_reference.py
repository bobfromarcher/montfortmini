import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from protected_reference import body_mask, protect, masked_policy
import qwen_reference_alignment as qwen


class ProtectedReferenceTests(unittest.TestCase):
    def test_original_face_and_clothing_pixels_survive_arbitrary_completion(self):
        pixels = np.arange(100 * 100 * 3, dtype='uint8').reshape(100, 100, 3)
        alpha = Image.fromarray(np.pad(np.full((75, 30), 255, dtype='uint8'), ((0, 25), (35, 35))))
        mask, record = body_mask(alpha, (100, 100), np.eye(3))
        completed, raw = protect(Image.fromarray(pixels), Image.new('RGB', (120, 120), 'red'), mask)
        actual = np.asarray(completed); outside = np.asarray(mask) == 0
        self.assertTrue(np.array_equal(actual[outside], pixels[outside]))
        self.assertTrue(np.all(actual[~outside] == [255, 0, 0]))
        self.assertGreater(record['first_edit_row'], 55)

    def test_mask_policy_changes_noise_region_and_restores_after_failure(self):
        builder = qwen.build_graph
        with self.assertRaises(RuntimeError):
            with masked_policy(Path('mask.png')):
                graph = qwen.build_graph()
                self.assertEqual(graph['13']['inputs']['latent_image'], ['17', 0])
                self.assertEqual(graph['17']['class_type'], 'SetLatentNoiseMask')
                raise RuntimeError('interrupted')
        self.assertIs(qwen.build_graph, builder)
