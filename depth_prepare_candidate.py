"""CPU-only geometry preprocessing; separate from frozen generator image layers."""
import io
from pathlib import Path
import zipfile
import modal

HERE = Path(__file__).parent
app = modal.App('montfortmini-depth-preprocessing')
image = (modal.Image.debian_slim(python_version='3.12')
         .pip_install('torch==2.9.1', index_url='https://download.pytorch.org/whl/cpu')
         .pip_install('transformers==4.57.6', 'huggingface-hub==0.36.0', 'Pillow==13.0.0', 'numpy==2.5.4')
         .add_local_file(HERE / 'depth_preprocessing.py', '/root/depth_preprocessing.py', copy=True)
         .run_commands('python /root/depth_preprocessing.py'))


@app.function(image=image, cpu=2, memory=8192, timeout=180,
              max_containers=1, min_containers=0, scaledown_window=2, retries=0)
def prepare_depth(source, guide):
    from depth_preprocessing import prepare
    return prepare(source, guide)


@app.local_entrypoint()
def main(source: str, guide: str, output: str):
    dest = Path(output); dest.mkdir(parents=True, exist_ok=False)
    data = prepare_depth.remote(Path(source).read_bytes(), Path(guide).read_bytes())
    (dest / 'guide-bundle.zip').write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if any(not (dest / i.filename).resolve().is_relative_to(dest.resolve()) for i in z.infolist()):
            raise ValueError('Unsafe depth evidence path')
        z.extractall(dest)
    print('CPU depth preparation complete; no GPU inference.', flush=True)
