# montfortmini

An independent, experimental video-editing workbench using open models and the official Comfy SDK. Upload a short video and one reference image, then replace a selected object or animate the reference character from the source motion.

It never calls Higgsfield's backend and does not contain their implementation, branding, assets, or weights. This is a functional alternative, not a claim of Genjutsu quality or feature parity.

## Features and limits

- **Object swap:** Wan2.1 VACE 1.3B, reference-guided inpainting, a drawn rectangle, and optional first/end rectangles interpolated along a straight path.
- **Motion transfer:** Wan Animate2 distilled int8 with source motion and a character reference.
- File uploads, prompt and seed controls, synchronized comparison, MP4 and exact workflow downloads.
- 17/33 frames at 8fps (2.125/4.125 seconds), up to 480px, one reference. Audio is omitted.
- 12MiB video, 4MiB reference, 16 megapixels per decoded image/frame. Short videos repeat their last frame.
- Official `comfy-sdk==0.5.0` workflow execution through `comfy-api-proxy==0.1.6` beside self-hosted ComfyUI.
- Modal backend: one GPU container maximum, zero warm GPU containers, no automatic generation retries, no persistent volumes.
- Optional local NVIDIA Docker backend using the same inference code.

The region uses a manual rectangle with linear interpolation. Both modes remain experimental. The [validation study](evaluation/FINDINGS.md) includes eight development/held-out synthetic and realistic clips, paired controls, and retained failures. Mirrored motion can produce duplicate arms; reference color, shading, and real-footage motion remain unreliable. Multiple subjects and long-term identity consistency are unvalidated.

The [evaluation harness](evaluation/README.md) records exact model/workflow provenance, raw versus composited outputs, resource use and a blinded review packet. The only production repair in that study honors display-rotation metadata before sizing frames and mapping masks.

The [quality follow-up](evaluation/quality/FINDINGS.md) adds controlled reference/framing experiments and four new prospective cases. The realistic fidelity/motion target remains unmet: object scale/lighting and side-view body motion still fail. Global center-cover fitting was rejected because it crops full-body references. The shipped follow-up repair saves confirmed SDK job receipts and allows bounded longer status reads, without automatic generation retries. [Reproduce the follow-up](evaluation/QUALITY.md), inspect its label-blinded packet, or watch the [108-second demonstration](submission/montfortmini-demo.mp4).

The [reference-preparation recovery study](evaluation/RECOVERY.md) implements and tests a pinned Klein → Qwen → Animate2 candidate. It improved a difficult development clip but failed identity on a new independent recording, so it was rejected for production. Exact stage provenance, frozen protocols and offline audit commands are included. The deployed inference path above remains the documented default.

Use one clear reference view with framing suited to the intended performance. Contact sheets can animate as multiple panels; tested headshots did not recover the source hand performance. Reference fitting and source framing are material limitations, not automatic subject tracking or pose reconstruction guarantees.

## Actual generation evidence

Original procedural fixtures and real generated clips are in [webapp/public/examples](webapp/public/examples). They are labeled as recorded proofs in the interface.

| Run | Size / frames | Inference-wrapper elapsed | Result |
| --- | --- | --- | --- |
| Corrected VACE SDK proof | 320x320 / 17 | 38.58s | Moving blue sphere replaces red cube |
| Animate2 SDK proof | 320x320 / 17 | 146.86s | New appearance and recognizable arm wave; background artifacts |
| Real-upload API object test | 480x480 / 17 | 70.10s | Uploaded clip/reference produce a blue sphere |
| Browser motion test | 480x480 / 17 | 92.44s | New character follows arm wave; downloads verified |

These ran on Modal L40S. Timings exclude some scheduling/build overhead and are not cost quotes.

Outside-mask preservation in the object **Finished** result comes from explicit compositing. Inspect **Raw result** to judge the model. Target pixels are erased to gray before VACE conditioning to prevent source identity leaking through its reactive branch. Region coordinates are mapped through letterboxing.

## Run with Modal

Requirements: Python 3.12+, Node 22.13+, a Modal account and enough included or authorized compute. Model weights and GPU dependencies are downloaded inside Modal.

```sh
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -r requirements.txt
python -m modal setup
```

Before running, check remaining included credit and set Modal's **net spend limit to $0** for credits-only execution. The app does not enforce your account's billing limit itself. Image builds, CPU, memory and cold starts also consume resources. No persistent volume is created.

Create a long random backend key. Save it as `OPENJUTSU_API_KEY` in a Modal secret named `openjutsu-site-api` through Modal's dashboard. Keep it private.

```sh
python -m modal deploy service.py
cd webapp
npm install
```

Copy `.dev.vars.example` to ignored `.dev.vars`. Set `OPENJUTSU_BACKEND_URL` to the URL printed by Modal, and `OPENJUTSU_API_KEY` to the same random key. For `npm run dev`, also copy those two settings into ignored `.env.local` before starting the server; Vinext's Node development runtime reads this file. `.dev.vars` supplies the Worker preview. Restart after changes. Never prefix secrets with `NEXT_PUBLIC_` or commit either file.

```sh
npm run dev
```

Open the printed loopback URL. The development server uses the starter's local mock sign-in. Production uses Sites owner-private access and server-side identity checks.

For your own Sites deployment, register your own project and replace `webapp/.openai/hosting.json`'s project ID through the official Sites setup workflow. Configure the same two runtime values through Sites settings, with the key marked secret. Do not put secrets in the hosting manifest. The checked-in project ID identifies this demonstration; it grants no access.

The backend requires its bearer key. `POST /jobs` accepts `mode`, `video_b64`, `reference_b64`, `prompt`, `seed`, `frames`, `bbox`, and `end_bbox`. Boxes are normalized `[left, top, width, height]`. Poll `GET /jobs?id=...`. Invalid workloads are rejected before GPU dispatch. Results are temporary: download them. A deployed service remains authorized independently of an expiring local CLI login.

## Fully local GPU option

Use Linux, or Windows with WSL2/Docker and NVIDIA Container Toolkit. Allow at least 60GB free disk, 32GB system RAM, and a 48GB GPU for the tested class of workload. Smaller cards may need changes; a 4GB laptop GPU is insufficient.

This Docker path is provided but **has not been executed on the available laptop**. Modal inference uses the same Python preparation and graph code.

```sh
docker build -f Dockerfile.local -t openjutsu-local .
# Set OPENJUTSU_API_KEY to your own random key in this shell first.
docker run --rm --gpus all -p 127.0.0.1:8000:8000 -e OPENJUTSU_API_KEY openjutsu-local
```

Set the webapp's ignored `.env.local` (and `.dev.vars` for Worker preview) backend URL to `http://127.0.0.1:8000` and its matching key, then run `npm install` and `npm run dev`. Loopback HTTP is allowed only in development. The local API permits one render at a time and keeps four results in memory. No Modal token or cloud inference is needed. Building downloads ComfyUI and model weights from official upstream repositories.

## Workflows and validation

```sh
python workflow.py > workflow-api.json
python -m unittest discover -s tests
cd webapp
npx tsc --noEmit
npm run build
```

Exports are Comfy API graphs, not standalone drag-and-drop UI workflows. They use bundled custom input nodes. Install the relevant `proof_inputs.py`, `motion_inputs.py`, or `media_pipeline.py` under ComfyUI `custom_nodes/` and provide the fixture folder described in their source to reuse them. The app downloads the exact graph with each generated result.

Standalone procedural proofs, after verifying credit/billing limits:

```sh
python -m modal run modal_probe.py --confirm-credits-only
python -m modal run motion_probe.py --confirm-credits-only
```

These save full source/raw/composite videos, frames, graph, manifest, package versions and execution log under ignored `results/`.

Ten production tests cover workload bounds, masks, reference-latent trimming, rotation, input validation, target erasure and receipt retention without resubmission on a polling failure. One separately labeled experimental-reference test covers the rejected crop candidate. Live checks verified authorization, invalid workloads, signed job identifiers and real-upload inference. Browser QA verified motion generation and MP4/workflow/provenance downloads; a later clean checkout verified installation, build, local sign-in and authenticated backend status.

## Licensing and provenance

Original application code and procedural fixtures: **MIT**, see [LICENSE](LICENSE). Retain bundled third-party notices, including `webapp/build/sites-vite-plugin.LICENSE`. ComfyUI and all dependencies keep their own licenses.

- ComfyUI commit: `5cc4b870094c89090db54bd8d12649dcaf89f2ba`.
- [VACE weights](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged), revision `123acf1cc74bccbb9bfff8ac1ee72edc08c2341d`.
- [Wan Animate2 weights](https://huggingface.co/Comfy-Org/Wan-Animate-2), revision `e7181fe1896b7f2ce34120d1a3663413548240d7`.
- Model filenames are pinned in `model_config.py` and `motion_model_config.py`. No weights are bundled. Review upstream Apache-2.0 notices and component terms.
- PyTorch/CUDA and SDK versions are pinned. Upstream Comfy requirements are resolved at build; full dependency locking remains future work.

Built toward the [Comfy open-source challenge](https://comfy.org/open-source-higgsfield). This app uses the official SDK's documented self-hosted integration. Organizer acceptance and prize eligibility are not guaranteed. A public social post and formal entry submission are separate steps.
