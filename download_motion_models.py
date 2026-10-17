from pathlib import Path
import shutil
from huggingface_hub import hf_hub_download
from motion_model_config import MODEL_REPO, MODEL_REVISION, MODEL_FILES

if __name__ == "__main__":
    if not Path("/opt/ComfyUI/main.py").is_file():
        raise RuntimeError("This is a remote container image-build helper")
    for folder,name in MODEL_FILES.items():
        source = hf_hub_download(MODEL_REPO,f"{folder}/{name}",revision=MODEL_REVISION,
                                 local_dir="/tmp/openjutsu-motion-download")
        target = Path("/opt/ComfyUI/models")/folder/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(source,target)
        print(f"Downloaded {folder}/{name}",flush=True)
