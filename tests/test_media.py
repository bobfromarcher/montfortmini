import base64
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from media_pipeline import validate_payload, erase_target


class MediaContracts(unittest.TestCase):
    def payload(self):
        return dict(mode="object-swap",video_b64=base64.b64encode(b"video").decode(),
                    reference_b64=base64.b64encode(b"image").decode(),
                    bbox=[.1,.2,.3,.4])

    def test_untrusted_requests_cannot_expand_work_or_escape_frame(self):
        cases = [dict(frames=81),dict(frames=True),dict(seed=-1),dict(seed=2**31),
                 dict(mode="arbitrary-node"),dict(bbox=[.9,.1,.3,.2]),
                 dict(bbox=[float("nan"),.1,.2,.2]),dict(end_bbox=[0,0,0,.4]),
                 dict(video_b64="not base64"),dict(prompt="a"*2001)]
        for invalid in cases:
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                validate_payload({**self.payload(),**invalid})

    def test_static_mask_defaults_to_same_end_position(self):
        request = validate_payload(self.payload())
        self.assertEqual(request["bbox"],request["end_bbox"])

    def test_target_erasure_blocks_source_identity_but_preserves_background(self):
        import numpy as np
        source = np.array([[[[1.,0.,0.],[0.,1.,0.]]]],dtype=np.float32)
        mask = np.array([[[1.,0.]]],dtype=np.float32)
        control = erase_target(source,mask)
        np.testing.assert_array_equal(control[0,0,0],[.5,.5,.5])
        np.testing.assert_array_equal(control[0,0,1],source[0,0,1])


if __name__ == "__main__":
    unittest.main()
