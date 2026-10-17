import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fidelity_candidate_media_pipeline import fit_reference


class ReferenceFraming(unittest.TestCase):
    def test_motion_has_no_synthetic_bands_and_object_retains_edges(self):
        from PIL import Image,ImageDraw
        source=Image.new('RGB',(100,50),'red')
        ImageDraw.Draw(source).rectangle((30,0,69,49),fill='blue')
        motion=fit_reference(source,(20,50),'motion-transfer')
        # The known blue central panel must fill the portrait, without gray bands.
        self.assertEqual(motion.getpixel((10,0)),(0,0,255))
        self.assertEqual(motion.getpixel((10,49)),(0,0,255))
        obj=fit_reference(source,(20,50),'object-swap')
        self.assertEqual(obj.getpixel((10,0)),(128,128,128))
        self.assertGreater(obj.getpixel((0,25))[0],200)
        self.assertGreater(obj.getpixel((19,25))[0],200)
        self.assertEqual(motion.size,obj.size)


if __name__=='__main__':unittest.main()
