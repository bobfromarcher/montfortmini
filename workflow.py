"""Small native ComfyUI VACE graph. No Higgsfield calls or partner nodes."""

from model_config import COMFY_COMMIT, MODEL_REPO, MODEL_REVISION, MODEL_FILES


def build_graph(width=320, height=320, frames=17, steps=20, seed=42):
    # Deliberately bounded feasibility workload, not the eventual product limits.
    if any(type(v) is not int for v in (width, height, frames, steps, seed)):
        raise ValueError("Test dimensions, frame count, steps, and seed must be integers")
    if not (128 <= width <= 480 and 128 <= height <= 480):
        raise ValueError("Proof dimensions must be between 128 and 480")
    if width % 16 or height % 16:
        raise ValueError("Dimensions must be multiples of 16")
    if not (5 <= frames <= 33 and (frames - 1) % 4 == 0):
        raise ValueError("Frames must be 4n+1, between 5 and 33")
    if not (1 <= steps <= 30 and 0 <= seed < 2**63):
        raise ValueError("Steps or seed outside the proof's limits")

    def node(kind, **inputs):
        return {"class_type": kind, "inputs": inputs}

    return {
        "1": node("UNETLoader", unet_name=MODEL_FILES["diffusion_models"], weight_dtype="default"),
        "2": node("CLIPLoader", clip_name=MODEL_FILES["text_encoders"], type="wan", device="default"),
        "3": node("VAELoader", vae_name=MODEL_FILES["vae"]),
        "4": node("CLIPTextEncode", clip=["2", 0], text=(
            "A perfectly round solid cobalt blue ball rolls slowly from left to right on a pale gray table. "
            "A single smooth blue sphere with a completely closed round surface, soft studio lighting, fixed camera.")),
        "5": node("CLIPTextEncode", clip=["2", 0], text=(
            "vase, jug, pot, cup, spout, handle, hole, opening, red cube, text, watermark, flicker, duplicate objects, blurry")),
        "6": node("OpenJutsuProofInputs", width=width, height=height, frames=frames),
        "7": node("WanVaceToVideo", positive=["4", 0], negative=["5", 0], vae=["3", 0],
                  width=width, height=height, length=frames, batch_size=1, strength=1.0,
                  control_video=["6", 0], control_masks=["6", 1], reference_image=["6", 2]),
        "8": node("ModelSamplingSD3", model=["1", 0], shift=8.0),
        "9": node("KSampler", model=["8", 0], seed=seed, steps=steps, cfg=5.0,
                  sampler_name="uni_pc", scheduler="simple", positive=["7", 0], negative=["7", 1],
                  latent_image=["7", 2], denoise=1.0),
        "10": node("TrimVideoLatent", samples=["9", 0], trim_amount=["7", 3]),
        "11": node("VAEDecode", samples=["10", 0], vae=["3", 0]),
        "12": node("SaveImage", images=["11", 0], filename_prefix="openjutsu-proof/raw"),
    }


def validate_graph(graph, schema):
    """Fail before sampling when the installed Comfy node contract differs."""
    for key, item in graph.items():
        kind = item["class_type"]
        if kind not in schema:
            raise ValueError(f"Missing Comfy node: {kind}")
        contract = schema[kind]
        inputs = item["inputs"]
        required = contract.get("input", {}).get("required", {})
        missing = set(required) - set(inputs)
        if missing:
            raise ValueError(f"{kind} missing inputs: {sorted(missing)}")
        for value in inputs.values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                upstream, slot = value
                if upstream not in graph:
                    raise ValueError(f"Dangling link in node {key}: {upstream}")
                outputs = schema[graph[upstream]["class_type"]].get("output", [])
                if type(slot) is not int or not 0 <= slot < len(outputs):
                    raise ValueError(f"Invalid output slot in node {key}")


if __name__ == "__main__":
    import json
    print(json.dumps(build_graph(), indent=2))

