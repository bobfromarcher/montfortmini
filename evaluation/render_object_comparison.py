"""Render the retained development failures at their original8fps; no inference."""
import argparse
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--factorial',action='store_true',help='Source/reference plus the four neutral/luma and instruction/description cells')
    parser.add_argument('--reference-luma',action='store_true',help='Source/reference plus old and normalized foreground-luma videos')
    parser.add_argument('--reference-chroma',action='store_true',help='Source/reference plus prior luma and reference-chromaticity videos')
    parser.add_argument('--color-prompt',action='store_true',help='Source/reference plus fixed-control two-word prompt ablation')
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
        if args.factorial:
            cases=[('Source recording',baseline/'inputs/source'),('Reference',baseline/'inputs/reference.png'),
                   ('Neutral control + instruction',baseline/stage),('Neutral control + description',root/'object-prompt'/stage),
                   ('Luma control + instruction',root/'object-luminance'/stage),('Luma control + description',root/'object-luminance-prompt'/stage)]
        if args.reference_luma:
            cases=[('Source recording',baseline/'inputs/source'),('Original reference',baseline/'inputs/reference.png'),
                   ('Previous luma + description',root/'object-luminance-prompt'/stage),
                   ('Foreground reference-luma normalization',root/'object-reference-luma'/stage)]
        if args.reference_chroma:
            cases=[('Source recording',baseline/'inputs/source'),('Original reference',baseline/'inputs/reference.png'),
                   ('Prior reference-luma control',root/'object-reference-luma'/stage),
                   ('Reference chromaticity control',root/'object-reference-chroma'/stage)]
        if args.color_prompt:
            cases=[('Source recording',baseline/'inputs/source'),('Original reference',baseline/'inputs/reference.png'),
                   ('Reference-chroma baseline: two green words',root/'object-reference-chroma'/stage),
                   ('Same control: two green words removed',root/'object-color-prompt'/stage)]
        columns=3 if args.factorial else 2
        for i in range(17):
            canvas=Image.new('RGB',(480*columns,700),'#101820');draw=ImageDraw.Draw(canvas)
            status='four fixed-seed conditions; quality verdict in review.json' if args.factorial else 'all candidates rejected'
            if args.reference_luma:status='foreground normalization; material gate remains unmet'
            if args.reference_chroma:status='fixed-seed chromaticity contrast; verdict in review.json'
            if args.color_prompt:status='only two color words removed; verdict in review.json'
            draw.text((10,8),f'montfortmini | {stage.upper()} | known development footage | frame{i}/16 | {status}',font=font,fill='white')
            for j,(label,frames) in enumerate(cases):
                x=(j%columns)*480;y=40+(j//columns)*304
                draw.text((x+8,y),label,font=font,fill='white')
                canvas.paste(Image.open(frames if frames.is_file() else frames/f'{i:04d}.png').convert('RGB'),(x,y+24))
            draw.text((8,651),'Source: Bombus terrestris rolling ball / Dona, Solvi, Kowalewska, Makela, MaBouDi & Chittka (2022), CC BY4.0.',font=small,fill='white')
            draw.text((8,671),'commons.wikimedia.org/wiki/File:Bombus_terrestris_rolling_ball.webm | Crop, resize, generated edits; no endorsement.',font=small,fill='white')
            canvas.save(folder/f'{i:04d}.png')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(args.output/f'{stage}-comparison.mp4')],check=True)


if __name__=='__main__':main()
