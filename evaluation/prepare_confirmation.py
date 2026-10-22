"""Reconstruct the already-observed CC0 research case; never a fresh holdout.

Downloads one public original, verifies SHA256, and crops the registered interval.
No models, GPU dispatch, or generation requests. FFmpeg encoding can vary by build.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).parent / 'recovery'
    provenance = json.loads((root / 'source-provenance.json').read_text(encoding='utf-8'))
    spec = json.loads((root / 'case-selection-freeze.json').read_text(encoding='utf-8'))['case']
    args.output.mkdir(parents=True, exist_ok=False)
    original = args.output / 'signer-original.webm'
    request = urllib.request.Request(provenance['imageinfo']['url'], headers={'User-Agent': 'montfortmini-research-reproduction/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response, original.open('wb') as target:
        size = 0
        for block in iter(lambda: response.read(1024 * 1024), b''):
            size += len(block)
            if size > 64 * 1024 * 1024:
                raise ValueError('Unexpectedly large source; stop before processing')
            target.write(block)
    if digest(original) != provenance['sha256']:
        raise ValueError('Original source SHA256 mismatch; do not render')
    reference = args.output / 'reference-original.png'
    shutil.copyfile(root / 'reference-original.png', reference)
    if digest(reference) != spec['sha256']['reference']:
        raise ValueError('Reference SHA256 mismatch; do not render')
    clip = args.output / 'signer-input-frozen.mp4'
    command = ['ffmpeg', '-y', '-loglevel', 'error', '-ss', '8', '-i', str(original),
               '-t', '4.125', '-an', '-vf', 'crop=650:750:850:80', '-c:v', 'libx264', '-crf', '18', str(clip)]
    subprocess.run(command, check=True, timeout=180)
    (args.output / 'cases.json').write_text(json.dumps({'signer': spec}, indent=2), encoding='utf-8')
    (args.output / 'reconstruction.json').write_text(json.dumps({
        'original_sha256': digest(original), 'reference_sha256': digest(reference),
        'derived_video_sha256': digest(clip), 'registered_video_sha256': spec['sha256']['video'],
        'encoded_bytes_match_registered': digest(clip) == spec['sha256']['video'],
        'ffmpeg_version': subprocess.check_output(['ffmpeg', '-version'], text=True),
        'command': command, 'split': 'Already observed research case, not a new holdout.',
        'publication': 'CC0 copyright declaration; no performer promotional likeness permission established. Research media excluded from the public submission.'
    }, indent=2), encoding='utf-8')
    print(args.output / 'cases.json')


if __name__ == '__main__':
    main()
