import unittest
from reference_alignment import source_canvas,identity_canvas
class AlignmentGeometry(unittest.TestCase):
 def test_source_orientation_and_reference_framing(self):
  self.assertEqual(source_canvas(720,1280),(768,1360))
  self.assertEqual(source_canvas(1280,720),(1360,768))
  self.assertEqual(source_canvas(1080,1080),(1024,1024))
  self.assertEqual(identity_canvas(511,477),(512,480))
  self.assertEqual(identity_canvas(1024,1536),(336,512))
 def test_unsupported_source_geometry_rejected(self):
  for shape in [(0,720),(720,0),(10000,100)]:
   with self.assertRaises(ValueError):source_canvas(*shape)
if __name__=='__main__':unittest.main()
