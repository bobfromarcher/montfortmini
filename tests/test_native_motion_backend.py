import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import numpy as np
from PIL import Image
from native_motion_backend import archive_prepared
from native_recipe_workflow import build_graph


class NativeAppInputsTests(unittest.TestCase):
    def test_app_fixture_keeps_pixels_and_compositor_masks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('source', 'masks'):
                (root/name).mkdir()
            source = Image.new('RGB', (16, 32), (11, 23, 37))
            source.save(root/'source/0000.png')
            Image.new('L', (16, 32), 255).save(root/'masks/0000.png')
            Image.new('RGB', (16, 32), (19, 41, 67)).save(root/'reference.png')
            (root/'settings.json').write_text(json.dumps({'frames':1,'width':16,'height':32}))
            payload = archive_prepared({'root':directory,'frames':1,'width':16,'height':32})
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                self.assertEqual(archive.read('source/0000.png'), (root/'source/0000.png').read_bytes())
                self.assertEqual(archive.read('reference.png'), (root/'reference.png').read_bytes())
                self.assertIn('masks/0000.png', archive.namelist())
                self.assertIn('pose/0000.png', archive.namelist())
                self.assertIn('face/0000.png', archive.namelist())
                with np.load(io.BytesIO(archive.read('conditioning.npz')), allow_pickle=False) as arrays:
                    self.assertEqual(arrays['source'].shape, (1,32,16,3))
                    self.assertTrue(np.all(arrays['mask']==1))
                    np.testing.assert_allclose(arrays['source'][0,0,0], np.array([11,23,37])/255)

    def test_app_sizes_keep_native_pose_and_face_conditioning(self):
        default = build_graph()
        resized = build_graph(width=320, height=480, frames=17)
        self.assertEqual(default['9'], resized['9'])
        self.assertEqual(resized['7']['inputs']['pose_video'], ['6',3])
        self.assertEqual(resized['7']['inputs']['face_video'], ['6',4])
        self.assertEqual(resized['7']['inputs']['length'], 17)
        self.assertEqual(resized['7']['inputs']['height'], 480)
        self.assertEqual(resized['9']['inputs']['steps'], 6)
