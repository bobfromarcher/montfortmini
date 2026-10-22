import hashlib
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import isolate_reference_subject as isolation


class ReferenceIsolationTests(unittest.TestCase):
    def test_native_input_alignment_and_upper_pixel_protection(self):
        observed = []
        class Detector:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def detect(self, image):
                observed.append(image.data.shape)
                mask = np.zeros(image.data.shape[:2], dtype='float32'); mask[:, :mask.shape[1]//2] = 1
                return NS(pose_landmarks=[[NS(x=.1, y=.2, visibility=1.)]],
                          segmentation_masks=[NS(numpy_view=lambda: mask)])
        fake = NS(Image=lambda **kw: NS(**kw), ImageFormat=NS(SRGB=1), __version__='fixture',
                  tasks=NS(BaseOptions=lambda **kw: kw, vision=NS(
                      PoseLandmarkerOptions=lambda **kw: kw, RunningMode=NS(IMAGE=1),
                      PoseLandmarker=NS(create_from_options=lambda options: Detector()))))
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); model = folder/'model'; model.write_bytes(b'fixture')
            Image.new('RGB', (650, 750), 'blue').save(folder/'base.png')
            Image.new('RGB', (650, 750), 'red').save(folder/'generated.png')
            mask = np.zeros((750, 650), dtype='uint8'); mask[570:] = 255
            Image.fromarray(mask).save(folder/'mask.png')
            with patch.dict(sys.modules, {'mediapipe': fake}), patch.object(isolation, 'MODEL_SHA', hashlib.sha256(b'fixture').hexdigest()):
                isolation.isolate(folder/'generated.png', folder/'base.png', folder/'mask.png', model, folder/'result')
            self.assertEqual(observed, [(736, 640, 3)])
            with Image.open(folder/'result/anchor.png') as im: result = np.asarray(im)
            self.assertTrue(np.all(result[:570] == [0, 0, 255]))
            self.assertTrue(np.all(result[600:, :300] == [255, 0, 0]))
            self.assertTrue(np.all(result[600:, 350:] == [0, 0, 255]))
