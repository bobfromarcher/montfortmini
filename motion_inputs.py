"""Original illustrated arm-wave inputs for the first motion-transfer proof."""
from pathlib import Path
import math


def draw_character(angle, blue=False, width=320, height=320):
    from PIL import Image, ImageDraw
    image = Image.new("RGB",(width,height),(232,228,216))
    d = ImageDraw.Draw(image)
    d.rectangle((0,280,320,320),fill=(203,198,185))
    skin = (231,178,137)
    shirt = (40,95,202) if blue else (51,141,79)
    d.ellipse((117,269,205,285),fill=(175,169,154))
    # Legs and shoes, a torso, and one stationary arm.
    d.line([(146,210),(141,269)],fill=(48,54,68),width=18)
    d.line([(175,210),(182,269)],fill=(48,54,68),width=18)
    d.rounded_rectangle((127,263,150,279),radius=5,fill=(33,35,40))
    d.rounded_rectangle((174,263,200,279),radius=5,fill=(33,35,40))
    d.rounded_rectangle((130,120,190,215),radius=14,fill=shirt)
    d.line([(136,134),(111,173),(117,205)],fill=skin,width=13)
    # The source's right arm rises from a relaxed position to a wave.
    shoulder = (185,136)
    elbow = (int(185+39*math.cos(angle)),int(136-39*math.sin(angle)))
    hand = (int(elbow[0]+29*math.cos(angle+.65)),int(elbow[1]-29*math.sin(angle+.65)))
    d.line([shoulder,elbow,hand],fill=skin,width=13)
    for x,y in (elbow,hand):
        d.ellipse((x-7,y-7,x+7,y+7),fill=skin)
    d.rectangle((150,107,170,127),fill=skin)
    d.ellipse((134,65,187,119),fill=skin)
    hair = (171,82,36) if blue else (53,43,32)
    d.pieslice((133,60,188,110),180,360,fill=hair)
    d.ellipse((146,86,150,91),fill=(40,37,32))
    d.ellipse((172,86,176,91),fill=(40,37,32))
    d.arc((151,91,172,108),0,180,fill=(115,67,53),width=2)
    return image


class OpenJutsuMotionInputs:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{}}
    RETURN_TYPES = ("IMAGE","IMAGE")
    FUNCTION = "load"
    CATEGORY = "OpenJutsu/proof"

    def load(self):
        import numpy as np
        import torch
        from PIL import Image
        root = Path("/tmp/openjutsu-fixture")
        (root/"source").mkdir(parents=True,exist_ok=True)
        (root/"masks").mkdir(parents=True,exist_ok=True)
        arrays = []
        for i in range(17):
            frame = draw_character(-.9+2.2*i/16)
            frame.save(root/"source"/f"{i:04d}.png")
            Image.new("L",(320,320),255).save(root/"masks"/f"{i:04d}.png")
            arrays.append(np.array(frame,dtype=np.float32)/255)
        reference = draw_character(-.9,blue=True)
        reference.save(root/"reference.png")
        return (torch.from_numpy(np.stack(arrays)),
                torch.from_numpy(np.array(reference,dtype=np.float32)/255)[None])


NODE_CLASS_MAPPINGS = {"OpenJutsuMotionInputs":OpenJutsuMotionInputs}
