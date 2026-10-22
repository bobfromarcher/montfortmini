import io
import json
import unittest
import zipfile
from PIL import Image
from native_recipe_fixture import validate_fixture


def fixture(masks=True, mask_size=(16, 16)):
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w') as z:
        z.writestr('settings.json', json.dumps({'frames': 1, 'width': 16, 'height': 16}))
        z.writestr('conditioning.npz', b'tensor contents irrelevant to file-completeness regression')
        for name in ('reference.png', 'source/0000.png', 'pose/0000.png', 'face/0000.png'):
            image = io.BytesIO(); Image.new('RGB', (16, 16)).save(image, format='PNG'); z.writestr(name, image.getvalue())
        if masks:
            image = io.BytesIO(); Image.new('L', mask_size, 255).save(image, format='PNG'); z.writestr('masks/0000.png', image.getvalue())
    return result.getvalue()


class PostprocessFixtureTests(unittest.TestCase):
    def test_mask_tensor_is_not_a_substitute_for_png_masks(self):
        with self.assertRaisesRegex(ValueError, 'masks/0000.png'):
            validate_fixture(fixture(masks=False), frames=1, width=16, height=16)

    def test_complete_postprocess_fixture_passes(self):
        self.assertTrue(validate_fixture(fixture(), frames=1, width=16, height=16)['postprocess_masks_present'])

    def test_wrong_mask_geometry_is_rejected_before_inference(self):
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            validate_fixture(fixture(mask_size=(8, 16)), frames=1, width=16, height=16)
