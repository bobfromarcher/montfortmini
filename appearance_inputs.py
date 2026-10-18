"""Original appearance-only input for a controlled conditioning ablation."""
from pathlib import Path
class OpenJutsuOriginalAppearance:
 @classmethod
 def INPUT_TYPES(cls):return {'required':{}}
 RETURN_TYPES=('IMAGE',)
 FUNCTION='load'
 CATEGORY='OpenJutsu/evaluation'
 def load(self):
  import numpy as np,torch
  from PIL import Image,ImageOps
  with Image.open(Path('/tmp/openjutsu-fixture/uploaded-reference')) as image:
   pixels=np.asarray(ImageOps.exif_transpose(image).convert('RGB'),dtype=np.float32)/255
  return (torch.from_numpy(pixels)[None],)
NODE_CLASS_MAPPINGS={'OpenJutsuOriginalAppearance':OpenJutsuOriginalAppearance}
