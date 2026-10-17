"""Runs inside the container image builder; never run on the user's laptop."""
from pathlib import Path
import shutil
from huggingface_hub import hf_hub_download
from model_config import MODEL_REPO, MODEL_REVISION, MODEL_FILES


if __name__ == "__main__":
    if not Path("/opt/ComfyUI/main.py").is_file():
        raise RuntimeError("This downloader is for the remote Comfy container, not local execution")
    for folder, name in MODEL_FILES.items():
        source = hf_hub_download(MODEL_REPO, f"split_files/{folder}/{name}",
                                 revision=MODEL_REVISION, local_dir="/tmp/openjutsu-download")
        destination = Path("/opt/ComfyUI/models") / folder / name
        destination.parent.mkdir(exist_ok=True, parents=True)
        shutil.move(source, destination)
        print(f"Downloaded {folder}/{name}", flush=True)
