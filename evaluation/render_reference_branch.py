"""Render source/reference/repeat/counterfactual evidence at original8fps."""
import argparse
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',type=Path,default=Path(__file__).parent/'reference-branch')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    parent=a.case.parent/'object-color-prompt'
    try:font=ImageFont.truetype('arial.ttf',16);small=ImageFont.truetype('arial.ttf',12)
    except OSError:font=ImageFont.load_default();small=font
    for stage in ('raw','composite'):
        folder=a.output/stage;folder.mkdir(exist_ok=True)
        cases=[('Source recording',a.case/'repeat/inputs/source'),
               ('Original reference: PNG preview',a.case/'repeat/inputs/branch-reference.png'),
               ('Counterfactual reference: PNG preview',a.case/'counterfactual/inputs/branch-reference.png'),
               ('Prior baseline: neutral color wording',parent/stage),
               ('Fresh repeat: original reference',a.case/'repeat'/stage),
               ('Only reference branch changed',a.case/'counterfactual'/stage)]
        for i in range(17):
            im=Image.new('RGB',(1440,700),'#101820');d=ImageDraw.Draw(im)
            d.text((8,8),f'montfortmini | {stage.upper()} | reference-branch diagnostic | frame {i}/16 | see FINDINGS.md',font=font,fill='white')
            for j,(label,path) in enumerate(cases):
                x=j%3*480;y=40+j//3*304;d.text((x+8,y),label,font=font,fill='white')
                im.paste(Image.open(path if path.is_file() else path/f'{i:04d}.png').convert('RGB'),(x,y+24))
            d.text((8,651),'Source: Bombus terrestris rolling ball / Dona, Solvi, Kowalewska, Makela, MaBouDi & Chittka (2022), CC BY4.0.',font=small,fill='white')
            d.text((8,671),'commons.wikimedia.org/wiki/File:Bombus_terrestris_rolling_ball.webm | Crop, resize, generated edits; NPZ reference tensors authoritative.',font=small,fill='white')
            im.save(folder/f'{i:04d}.png')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(a.output/f'{stage}-comparison.mp4')],check=True)


if __name__=='__main__':main()
