"""Render the retained development failures at their original8fps; no inference."""
import argparse
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).parent
    baseline=root/'quality/samples/new-real-object__candidate__s42'
    try:font=ImageFont.truetype('arial.ttf',16);small=ImageFont.truetype('arial.ttf',12)
    except OSError:font=ImageFont.load_default();small=font
    for stage in ('raw','composite'):
        folder=args.output/stage;folder.mkdir(exist_ok=True)
        cases=[('Source',baseline/'inputs/source'),
               ('Original baseline: oversized green target',baseline/stage),
               ('Registered reference: FAIL wrong yellow target',root/'object-reference'/stage),
               ('Output-description prompt: FAIL scale and shape',root/'object-prompt'/stage)]
        for i in range(17):
            canvas=Image.new('RGB',(960,700),'#101820');draw=ImageDraw.Draw(canvas)
            draw.text((10,8),f'montfortmini | {stage.upper()} | known development footage | frame{i}/16 | all candidates rejected',font=font,fill='white')
            for j,(label,frames) in enumerate(cases):
                x=(j%2)*480;y=40+(j//2)*304
                draw.text((x+8,y),label,font=font,fill='white')
                canvas.paste(Image.open(frames/f'{i:04d}.png').convert('RGB'),(x,y+24))
            draw.text((8,651),'Source: Bombus terrestris rolling ball / Dona, Solvi, Kowalewska, Makela, MaBouDi & Chittka (2022), CC BY4.0.',font=small,fill='white')
            draw.text((8,671),'commons.wikimedia.org/wiki/File:Bombus_terrestris_rolling_ball.webm | Crop, resize, generated edits; no endorsement.',font=small,fill='white')
            canvas.save(folder/f'{i:04d}.png')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(args.output/f'{stage}-comparison.mp4')],check=True)


if __name__=='__main__':main()
