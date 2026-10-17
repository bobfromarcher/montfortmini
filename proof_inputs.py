"""Original procedural fixtures; no downloaded artwork or personal footage."""
from pathlib import Path


def create_fixture(directory, width=320, height=320, frames=17):
    from PIL import Image, ImageDraw

    directory = Path(directory)
    for name in ("source", "masks"):
        (directory / name).mkdir(parents=True, exist_ok=True)
    size = int(min(width, height) * 0.22)
    cy = int(height * 0.56)
    for i in range(frames):
        cx = int(width * (0.32 + 0.36 * i / (frames - 1)))
        image = Image.new("RGB", (width, height), (218, 224, 230))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, int(height * 0.63), width, height), fill=(187, 196, 206))
        draw.ellipse((cx-size//2, cy+size//2-4, cx+size, cy+size//2+12), fill=(150, 158, 169))
        draw.rectangle((cx-size//2, cy-size//2, cx+size//2, cy+size//2), fill=(193, 43, 41))
        draw.polygon([(cx-size//2,cy-size//2),(cx-size//4,cy-size//2-12),
                      (cx+size//2+12,cy-size//2-12),(cx+size//2,cy-size//2)], fill=(231, 83, 70))
        draw.polygon([(cx+size//2,cy-size//2),(cx+size//2+12,cy-size//2-12),
                      (cx+size//2+12,cy+size//2-12),(cx+size//2,cy+size//2)], fill=(131, 28, 31))
        image.save(directory / "source" / f"{i:04d}.png")
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).rectangle((cx-size//2-14,cy-size//2-22,
                                       cx+size+4,cy+size//2+18), fill=255)
        mask.save(directory / "masks" / f"{i:04d}.png")
    reference = Image.new("RGB", (width, height), (218, 224, 230))
    draw = ImageDraw.Draw(reference)
    draw.rectangle((0, int(height*.63), width,height), fill=(187,196,206))
    cx = width // 2
    radius = size // 2 + 4
    draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(15,68,158))
    for r in range(radius-1, 0, -1):
        bright = int(110 * (1-r/radius))
        draw.ellipse((cx-r-3,cy-r-5,cx+r-3,cy+r-5), fill=(25+bright//3,90+bright//2,190+bright//2))
    reference.save(directory / "reference.png")


class OpenJutsuProofInputs:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "width": ("INT", {"default":320,"min":128,"max":480,"step":16}),
            "height": ("INT", {"default":320,"min":128,"max":480,"step":16}),
            "frames": ("INT", {"default":17,"min":5,"max":33,"step":4}),
        }}
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    FUNCTION = "load"
    CATEGORY = "OpenJutsu/proof"

    def load(self, width, height, frames):
        import numpy as np
        import torch
        from PIL import Image
        from workflow import build_graph
        build_graph(width=width, height=height, frames=frames)
        root = Path("/tmp/openjutsu-fixture")
        create_fixture(root, width, height, frames)
        images = [np.array(Image.open(root/"source"/f"{i:04d}.png"),dtype=np.float32)/255 for i in range(frames)]
        masks = [np.array(Image.open(root/"masks"/f"{i:04d}.png"),dtype=np.float32)/255 for i in range(frames)]
        reference = np.array(Image.open(root/"reference.png"),dtype=np.float32)/255
        source = np.stack(images)
        mask = np.stack(masks)
        # White means regenerate. Erase the old target in the control stream;
        # the native VACE node encodes both inactive and reactive pixels.
        control = source * (1-mask[...,None]) + 0.5 * mask[...,None]
        return (torch.from_numpy(control), torch.from_numpy(mask),
                torch.from_numpy(reference)[None])


NODE_CLASS_MAPPINGS = {"OpenJutsuProofInputs": OpenJutsuProofInputs}

