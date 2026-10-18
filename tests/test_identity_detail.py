import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identity_detail import identity_canvas, MAX_IDENTITY_PIXELS
from reference_alignment import identity_canvas as legacy_canvas
from detail_reference_alignment import detail_policy
import reference_alignment
import qwen_reference_alignment


class IdentityDetail(unittest.TestCase):
    def test_original_portrait_pixels_survive_native_reference_preparation(self):
        # Fine real pixels disappear if the image is first reduced to336x512.
        yy, xx = np.indices((1536, 1024))
        pattern = (((xx // 2 + yy // 2) % 2) * 255).astype(np.uint8)
        original = Image.fromarray(np.stack([pattern] * 3, axis=-1))
        target = identity_canvas(*original.size)
        self.assertEqual(target, (672, 1024))
        direct = np.asarray(original.resize(target, Image.Resampling.LANCZOS), dtype=float)
        reduced = original.resize(legacy_canvas(*original.size), Image.Resampling.LANCZOS)
        fabricated = np.asarray(reduced.resize(target, Image.Resampling.NEAREST), dtype=float)
        self.assertGreater(float(np.mean(np.abs(direct - fabricated))), 20)
        self.assertGreater(float(direct.std()), float(fabricated.std()) * 2)

    def test_small_inputs_are_not_pretended_to_have_more_detail(self):
        self.assertEqual(identity_canvas(384, 320), legacy_canvas(384, 320))
        self.assertEqual(identity_canvas(511, 477), (512, 480))
        for shape in [(1024, 1536), (4096, 4096), (2048, 512), (512, 2048)]:
            w, h = identity_canvas(*shape)
            self.assertLessEqual(w * h, MAX_IDENTITY_PIXELS)
            self.assertEqual((w % 16, h % 16), (0, 0))
            old_w, old_h = legacy_canvas(*shape)
            self.assertEqual(w * old_h, h * old_w)

    def test_ablation_does_not_leak_into_frozen_helpers_after_failure(self):
        a, b = reference_alignment.identity_canvas, qwen_reference_alignment.identity_canvas
        with self.assertRaisesRegex(RuntimeError, 'interrupted'):
            with detail_policy('qwen'):
                self.assertIs(reference_alignment.identity_canvas, a)
                self.assertIs(qwen_reference_alignment.identity_canvas, identity_canvas)
                raise RuntimeError('interrupted')
        self.assertIs(reference_alignment.identity_canvas, a)
        self.assertIs(qwen_reference_alignment.identity_canvas, b)
