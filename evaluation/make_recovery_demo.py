"""Update the cleared 108-second demo with a frozen regression and honest limits.

Uses only original procedural artwork/interface. Human research media is excluded.
The source model clips play at 8fps with repeated display frames, no interpolation.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from make_demo import base, text, encode_still, MUTED


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-assets', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    assets = args.output / 'demo-assets'
    assets.mkdir()
    # Reuse unchanged UI/default-engine demonstrations with their original clearance.
    for p in args.previous_assets.iterdir():
        if p.is_file() and p.name != 'concat.txt':
            shutil.copyfile(p, assets / p.name)
    run = args.candidate
    canvas = base('Frozen regression — same two-arm source',
                  'Experimental Klein → Qwen → Wan candidate. This is a known regression clip, not held-out footage.')
    draw = ImageDraw.Draw(canvas)
    for col, label in enumerate(('Uploaded reference', 'Source', 'Candidate raw', 'Candidate finished')):
        text(draw, (45 + col * 306, 202), label, 21)
    reference = run / 'original-reference.png'
    with Image.open(reference) as image:
        canvas.paste(ImageOps.pad(image.convert('RGB'), (280, 300), color='#292b33'), (45, 245))
    text(draw, (45, 579), 'The new real-recording identity test failed. Candidate was not promoted.', 23, width=90)
    text(draw, (45, 619), 'Actual outputs loop at 8fps; no interpolation, face repair or frame replacement.', 21, width=94, fill=MUTED)
    canvas.save(assets / '04.png')
    command = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', '24', '-i', str(assets / '04.png')]
    for name in ('source.mp4', 'generated.mp4', 'composite.mp4'):
        command.extend(['-stream_loop', '-1', '-i', str(run / name)])
    filters = []
    previous = '0:v'
    for j in range(1, 4):
        filters.append(f'[{j}:v]scale=280:300:force_original_aspect_ratio=decrease,pad=280:300:(ow-iw)/2:(oh-ih)/2:color=0x292b33,fps=24[v{j}]')
        filters.append(f'[{previous}][v{j}]overlay={45+j*306}:245[out{j}]')
        previous = f'out{j}'
    command += ['-filter_complex', ';'.join(filters), '-map', f'[{previous}]', '-t', '16', '-an',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p', str(assets / '04.mp4')]
    subprocess.run(command, check=True, timeout=240)
    canvas = base('Validation result: realistic quality target unmet',
                  'The shipped default remains unchanged. Inspect the rejected candidate and retained failures.')
    draw = ImageDraw.Draw(canvas)
    text(draw, (65, 225),
         '• Development framing and hand performance improved\n'
         '• Fresh recording lost reference glasses, hair and facial identity\n'
         '• Error already visible in reference-preparation stages\n'
         '• Exact graphs, hashes, logs and offline audit commands retained\n'
         '• Independent professional review and GPU reproduction pending',
         28, width=82, spacing=17)
    canvas.save(assets / '06.png')
    encode_still(assets / '06.png', 14, assets / '06.mp4')
    listing = assets / 'concat.txt'
    listing.write_text(''.join(f"file '{i:02d}.mp4'\n" for i in range(8)), encoding='utf-8')
    movie = args.output / 'montfortmini-demo.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-c', 'copy', '-movflags', '+faststart', str(movie)], check=True, timeout=120)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', str(movie)], text=True))
    duration = float(probe['format']['duration'])
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    if duration > 120 or int(stream['nb_read_frames']) != 2592:
        raise ValueError('Demo duration/frame verification failed')
    metadata = {'duration_seconds': duration, 'decoded_video_frames': int(stream['nb_read_frames']),
                'sha256': hashlib.sha256(movie.read_bytes()).hexdigest(),
                'changed_segments': ['04: frozen synthetic regression', '06: recovery-study finding'],
                'unchanged_assets': 'Original 108-second demo; see prior-demo-provenance.json',
                'candidate_assets': {name: hashlib.sha256((run / name).read_bytes()).hexdigest()
                                     for name in ('original-reference.png', 'source.mp4', 'generated.mp4', 'composite.mp4', 'manifest.json')},
                'rights': 'Original MIT procedural art/interface and its generated derivatives only. No human research footage, private likenesses or Genjutsu media.',
                'processing': 'Contain resizing, layout, repeated 8fps playback displayed at24fps and H264 encoding. No frame interpolation or repair.', 'audio': 'none; captioned'}
    (args.output / 'demo-provenance.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps({'duration': duration, 'frames': stream['nb_read_frames'], 'file': str(movie)}))


if __name__ == '__main__':
    main()
