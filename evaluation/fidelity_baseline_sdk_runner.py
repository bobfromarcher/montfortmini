"""Supported Comfy SDK bridge for a self-hosted, loopback-only ComfyUI instance.

Optional until the initial native API proof succeeds. Run the proxy beside Comfy:
    comfy-api-proxy --comfyui http://127.0.0.1:8188 --port 8189
Install comfy-api-proxy==0.1.6 and comfy-sdk==0.5.0 in that environment.
"""
import os
from pathlib import Path


def run_with_sdk(graph, output_directory, timeout=480):
    from comfy_sdk import Comfy

    os.environ["COMFY_BASE_URL"] = "http://127.0.0.1:8189"
    os.environ.pop("COMFY_API_KEY", None)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    with Comfy(timeout=30) as client:
        workflow = client.workflows.from_json(graph)
        job = client.run(workflow, timeout=timeout)
        files = []
        for output in job.outputs:
            name = Path(output.name).name
            if not name or name in (".", ".."):
                raise ValueError("Invalid Comfy output filename")
            path = output_directory / name
            output.to_file(str(path))
            files.append(str(path))
        return {"job_id":job.id,"status":str(job.status),"files":files}
