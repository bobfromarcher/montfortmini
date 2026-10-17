import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow import build_graph
from proof_inputs import create_fixture


class ProofLimits(unittest.TestCase):
    def test_rejects_costly_or_invalid_workloads(self):
        for args in ({"width":1920}, {"frames":81}, {"steps":100},
                     {"width":319}, {"frames":16}, {"frames":True}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                build_graph(**args)

    def test_reference_latents_are_removed_before_decoding(self):
        graph = build_graph()
        trim = graph["10"]
        self.assertEqual(trim["class_type"], "TrimVideoLatent")
        self.assertEqual(trim["inputs"]["trim_amount"], ["7",3])
        self.assertEqual(graph["11"]["inputs"]["samples"], ["10",0])

    def test_fixture_mask_covers_every_changed_source_pixel(self):
        from PIL import Image, ImageChops, ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            create_fixture(temp)
            root = Path(temp)
            self.assertEqual(len(list((root/"source").glob("*.png"))),17)
            background = Image.new("RGB",(320,320),(218,224,230))
            ImageDraw.Draw(background).rectangle((0,int(320*.63),320,320),fill=(187,196,206))
            centroids = []
            for i in range(17):
                image = Image.open(root/"source"/f"{i:04d}.png")
                mask = Image.open(root/"masks"/f"{i:04d}.png")
                changed = ImageChops.difference(image, background).convert("L").point(lambda p:255 if p else 0)
                leak = ImageChops.multiply(changed,ImageChops.invert(mask))
                self.assertIsNone(leak.getbbox(), f"Frame {i} has changes outside its mask")
                left,top,right,bottom = mask.getbbox()
                centroids.append((left+right)/2)
            self.assertEqual(centroids,sorted(centroids))
            self.assertGreater(centroids[-1]-centroids[0],100)
            with Image.open(root/"reference.png") as reference:
                self.assertEqual(reference.size,(320,320))


if __name__ == "__main__":
    unittest.main()
