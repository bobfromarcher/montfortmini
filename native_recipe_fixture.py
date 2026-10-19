"""Validate file artifacts required after inference as well as model inputs."""
import io
import json
from pathlib import PurePosixPath
import zipfile
from PIL import Image


def validate_fixture(payload, *, frames, width, height):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise ValueError('Duplicate fixture archive entries')
        if any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts for n in names):
            raise ValueError('Unsafe fixture path')
        required = {'settings.json', 'conditioning.npz', 'reference.png'}
        required.update(f'{folder}/{i:04d}.png' for folder in ('source', 'masks', 'pose', 'face') for i in range(frames))
        missing = sorted(required - set(names))
        if missing:
            raise ValueError(f'Incomplete fixture: {len(missing)} missing files; first: {missing[0]}')
        settings = json.loads(archive.read('settings.json'))
        if any(settings.get(k) != v for k, v in {'frames': frames, 'width': width, 'height': height}.items()):
            raise ValueError('Fixture dimensions/frame count differ from graph')
        for i in range(frames):
            for folder in ('source', 'masks'):
                with Image.open(io.BytesIO(archive.read(f'{folder}/{i:04d}.png'))) as image:
                    if image.size != (width, height):
                        raise ValueError(f'Fixture {folder} image dimensions differ from graph')
        return {'frames': frames, 'width': width, 'height': height,
                'required_files_present': len(required), 'postprocess_masks_present': True}
