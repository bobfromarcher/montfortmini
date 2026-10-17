"""One credit-bounded character motion proof; no public endpoint."""
import io
import zipfile
from pathlib import Path
import datetime
import modal
from modal_probe import base_image, masked_replacement
from motion_workflow import build_graph
from motion_model_config import MODEL_REPO, MODEL_REVISION

HERE = Path(__file__).parent
app = modal.App("openjutsu-motion-feasibility")
motion_base_image = (base_image
    .add_local_file(HERE/"motion_model_config.py","/root/motion_model_config.py",copy=True)
    .add_local_file(HERE/"download_motion_models.py","/root/download_motion_models.py",copy=True)
    .run_commands("timeout 900 python /root/download_motion_models.py")
)
image = (motion_base_image
    .add_local_file(HERE/"workflow.py","/root/workflow.py")
    .add_local_file(HERE/"sdk_runner.py","/root/sdk_runner.py")
    .add_local_file(HERE/"modal_probe.py","/root/modal_probe.py")
    .add_local_file(HERE/"motion_workflow.py","/root/motion_workflow.py")
    .add_local_file(HERE/"proof_inputs.py","/root/proof_inputs.py")
    .add_local_file(HERE/"motion_inputs.py","/opt/ComfyUI/custom_nodes/openjutsu_motion.py")
)


@app.function(image=image,gpu="L40S",cpu=2,memory=32768,
              timeout=600,startup_timeout=180,max_containers=1,
              min_containers=0,scaledown_window=2,retries=0)
def transfer_motion():
    return masked_replacement.local(build_graph(),{
        "repo":MODEL_REPO,"revision":MODEL_REVISION,"mode":"motion-transfer"})


@app.local_entrypoint()
def main(confirm_credits_only:bool=False):
    if not confirm_credits_only:
        raise RuntimeError("Verify included credits and $0 net spend, then pass --confirm-credits-only")
    payload = transfer_motion.remote()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = HERE/"results"/(stamp+"-motion")
    target.mkdir(parents=True,exist_ok=False)
    (target/"proof.zip").write_bytes(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if any(not (target/i.filename).resolve().is_relative_to(target.resolve()) for i in archive.infolist()):
            raise ValueError("Unsafe archive path")
        archive.extractall(target)
    print(f"Motion output ready for visual review: {target}")
