# montfortmini

**Open-source video workbench · developer-alpha candidate.** Reference-guided
object replacement and character motion transfer with ComfyUI and the official
Comfy SDK. The current candidate is on [`codex/validation`](https://github.com/bobfromarcher/montfortmini/tree/codex/validation);
the default branch currently contains an older pipeline. No alpha release tag
has been published yet.

Our development priority is **identity consistency**: preserving a character's
facial features and an object's defining appearance through motion. Exact facial
likeness, turns/occlusion and consistency across separate shots remain unproved.
This independent implementation does not call Higgsfield or contain its backend
code. No Genjutsu parity or superiority is claimed.

## Who can use this today

Technical users can run short experiments on their own GPU or their own Modal
account. The measured native-motion allocation was an L40S48GB with64GB requested
system memory. That is a successful allocation, not a proven minimum. The full
local Docker GPU path has not been independently executed. A4GB laptop cannot
reproduce the measured workload.

The hosted studio is currently owner-private. There is no public free-generation
service, and repository access does not grant access to the maintainer's compute.
Use the setup below with your own backend and credentials. Public announcement
and alpha-release drafts are in [submission/RELEASE-PLAN.md](submission/RELEASE-PLAN.md).

## Capabilities and current limits

| Capability | Working path | Evidence and limits |
|---|---|---|
| Character motion transfer | Native Wan2.2-Animate14B, pinned whole-body/hand pose and face controls, Lightx2v/relighting adapters | Actual app-path video completed. Broad reference attributes and4/4 motion events provisionally retained on one recording. Face/glasses proportions and fingers remain imperfect; exact identity/generalization unproved. |
| Reference-guided object replacement | Wan2.1 VACE1.3B, manual rectangular region and optional linear start/end positions | Simple synthetic replacements run. Realistic reference fidelity/material/lighting still fail the full quality gate. No AI object tracking. |
| Inspection/export | Source, raw and composited video; exact executed workflow and run details | Composite background preservation comes from the compositor. Evaluate the raw output separately. |

Inputs: one reference;17/33frames at8fps (2.125/4.125s); motion up to480x560,
objects up to480x480;12MiB video/4MiB reference; no audio. Use a single clear
performer and a complete character reference for motion. Automatic portrait
completion, long clips and multi-person handling are not validated.

## Start here

```sh
git clone --branch codex/validation https://github.com/bobfromarcher/montfortmini.git
cd montfortmini
```

Choose **Run with Modal** below for your own cloud account, or **Fully local GPU
option** for the provided Docker path. Generation consumes your compute; model
build/download and CPU preparation also have costs. The local UI uses a mock
sign-in during development. Production Sites hosting uses its access gate and
requires separate configuration.

## Watch and assess the actual evidence

- [Native motion app integration](evaluation/native-motion-service/FINDINGS.md): current app recipe and retained limitations. Human-source research footage is private because public promotional likeness clearance is outstanding.
- [Reference-only sensitivity](evaluation/reference-branch/FINDINGS.md): active but weak reference response with text/control fixed; both outputs fail appearance.
- [Latest guidance contrast](evaluation/guidance-balance/FINDINGS.md): CFG1 rejected; beige becomes red despite identical conditioning. Includes public licensed raw/composite comparisons.
- [Earlier procedural examples](webapp/public/examples): actual recorded synthetic proofs from the older recipes, not current native-face validation.
- [Earlier108-second demo](submission/montfortmini-demo.mp4): archival demonstration predating the native motion integration. An updated cleared demo remains a release/submission gate.
- [Alpha notes](submission/ALPHA-RELEASE-NOTES.md), [launch plan](submission/RELEASE-PLAN.md), [competition checklist](submission/REQUIREMENTS-AUDIT.md).

All earlier failed studies remain under `evaluation/`. Current measured quality
is experimental. A runnable technical alpha and a passing realistic-quality
candidate are separate milestones.

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

These Docker paths **have not been executed on the available laptop**. The base
image retains the older Animate2 motion recipe. Add the native extension below
to use the same native preparation and graph functions as the current Modal app.
Allow additional disk space for approximately23GB of native/pose weights,
their download cache and image layers, and64GB system RAM for the measured
cloud allocation; local hardware requirements are not independently established.

```sh
docker build -f Dockerfile.local -t openjutsu-local .
# Set OPENJUTSU_API_KEY to your own random key in this shell first.
docker run --rm --gpus all -p 127.0.0.1:8000:8000 -e OPENJUTSU_API_KEY openjutsu-local
```

For the native motion recipe, after building `openjutsu-local`:

```sh
docker build -f Dockerfile.native -t montfortmini-native .
docker run --rm --gpus all -p 127.0.0.1:8000:8000 -e OPENJUTSU_API_KEY montfortmini-native
```

The extension installs pinned ONNX preprocessing dependencies, verifies native
model downloads, and installs the explicit pose/face input node. Local execution
uses `.local()` calls and requires no Modal account. This is a provided
reproduction path, not a claimed independently tested GPU installation.

Set the webapp's ignored `.env.local` (and `.dev.vars` for Worker preview) backend URL to `http://127.0.0.1:8000` and its matching key, then run `npm install` and `npm run dev`. Loopback HTTP is allowed only in development. The local API permits one render at a time and keeps four results in memory. No Modal token or cloud inference is needed. Building downloads ComfyUI and model weights from official upstream repositories.

## Workflows and validation

```sh
python workflow.py > workflow-api.json
python -m unittest discover -s tests
cd webapp
npx tsc --noEmit
npm run build
```

Exports are Comfy API graphs, not standalone drag-and-drop UI workflows. They use bundled custom input nodes. Native motion needs `explicit_motion_inputs.py` and its prepared `conditioning.npz` containing source, mask, reference, pose and face arrays; raw RGB is not its pose input. Other recipes use `proof_inputs.py`, `motion_inputs.py`, or `media_pipeline.py`. The app downloads the exact graph with each result. See the native findings for executable offline audits and controlled replay.

Standalone procedural proofs, after verifying credit/billing limits:

```sh
python -m modal run modal_probe.py --confirm-credits-only
python -m modal run motion_probe.py --confirm-credits-only
```

These save full source/raw/composite videos, frames, graph, manifest, package versions and execution log under ignored `results/`.

The current61-test CPU suite covers workload bounds, masks, reference-latent trimming, rotation, input validation, receipt retention and research-conditioning regressions. It passes from a fresh Git extraction using existing dependencies; this is not an independent GPU reproduction. Live checks verified authorization, invalid workloads, signed job identifiers and real-upload inference. Browser QA verified motion generation and MP4/workflow/provenance downloads; a later clean checkout verified installation, build, local sign-in and authenticated backend status.

## Licensing and provenance

Original application code and procedural fixtures: **MIT**, see [LICENSE](LICENSE). Retain bundled third-party notices, including `webapp/build/sites-vite-plugin.LICENSE`. ComfyUI and all dependencies keep their own licenses.

- ComfyUI commit: `5cc4b870094c89090db54bd8d12649dcaf89f2ba`.
- [VACE weights](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged), revision `123acf1cc74bccbb9bfff8ac1ee72edc08c2341d`.
- [Wan Animate2 weights](https://huggingface.co/Comfy-Org/Wan-Animate-2), revision `e7181fe1896b7f2ce34120d1a3663413548240d7`.
- Model filenames are pinned in `model_config.py` and `motion_model_config.py`. No weights are bundled. Review upstream Apache-2.0 notices and component terms.
- Current native-motion model revisions, sizes and SHA256 are in `native_recipe_models.py`; pinned pose source/weights and Apache notices are in `vendor/wan_animate/provenance.json`. The converted checkpoint card declares Apache2; the generic conversion repository lacks a global license declaration. The adapter README attributes its Apache upstreams; this declaration gap remains disclosed. No converted weights are redistributed.
- PyTorch/CUDA and SDK versions are pinned. Upstream Comfy requirements are resolved at build; full dependency locking remains future work.

Built toward the [Comfy open-source challenge](https://comfy.org/open-source-higgsfield). This app uses the official SDK's documented self-hosted integration. Organizer acceptance and prize eligibility are not guaranteed. A public social post and formal entry submission are separate steps.
