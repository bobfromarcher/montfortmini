# montfortmini

An independent, experimental video-editing workbench using open models and the official Comfy SDK. Upload a short video and one reference image, then replace a selected object or animate the reference character from the source motion.

It never calls Higgsfield's backend and does not contain their implementation, branding, assets, or weights. This is a functional alternative, not a claim of Genjutsu quality or feature parity.

## Features and limits

- **Object swap:** Wan2.1 VACE 1.3B, reference-guided inpainting, a drawn rectangle, and optional first/end rectangles interpolated along a straight path.
- **Motion transfer:** native Wan2.2-Animate14B with pinned whole-body/hand pose and face controls, converted checkpoint, Lightx2v acceleration and relighting adapters. Use single-person footage and a complete character reference. Portrait completion is not automatic.
- File uploads, prompt and seed controls, synchronized comparison, MP4 and exact workflow downloads.
- 17/33 frames at 8fps (2.125/4.125 seconds), motion up to480×560, objects up to480×480, one reference. Audio is omitted.
- 12MiB video, 4MiB reference, 16 megapixels per decoded image/frame. Short videos repeat their last frame.
- Official `comfy-sdk==0.5.0` workflow execution through `comfy-api-proxy==0.1.6` beside self-hosted ComfyUI.
- Modal backend: one GPU container maximum, zero warm GPU containers, no automatic generation retries, no persistent volumes.
- Optional local NVIDIA Docker recipes, including a native-motion extension; full local GPU execution remains unverified.

The region uses a manual rectangle with linear interpolation. Both modes remain experimental. The [validation study](evaluation/FINDINGS.md) includes eight development/held-out synthetic and realistic clips, paired controls, and retained failures. Mirrored motion can produce duplicate arms; reference color, shading, and real-footage motion remain unreliable. Multiple subjects and long-term identity consistency are unvalidated.

The [evaluation harness](evaluation/README.md) records exact model/workflow provenance, raw versus composited outputs, resource use and a blinded review packet. The only production repair in that study honors display-rotation metadata before sizing frames and mapping masks.

The [quality follow-up](evaluation/quality/FINDINGS.md) adds controlled reference/framing experiments and four new prospective cases. The realistic fidelity/motion target remains unmet: object scale/lighting and side-view body motion still fail. Global center-cover fitting was rejected because it crops full-body references. The shipped follow-up repair saves confirmed SDK job receipts and allows bounded longer status reads, without automatic generation retries. [Reproduce the follow-up](evaluation/QUALITY.md), inspect its label-blinded packet, or watch the [108-second demonstration](submission/montfortmini-demo.mp4).

The [reference-preparation recovery study](evaluation/RECOVERY.md) implements and tests a pinned Klein → Qwen → Animate2 candidate. It improved a difficult development clip but failed identity on a new independent recording, so it was rejected for production. Exact stage provenance, frozen protocols and offline audit commands are included. The deployed inference path above remains the documented default.

The [focused correction cycle](evaluation/detail-cycle/FINDINGS.md) fixes loss of original reference detail in an optional research helper. Paired stills restore facial attributes but fail identity/clothing/pose gates. Both failures are retained; no new video claim or production promotion follows.

A subsequent [pose-only alternative](evaluation/pose-reference/FINDINGS.md) removes the two-editor cascade and source-person appearance from reference preparation. Native Qwen editing receives an estimated skeleton and the original identity. Its reference still loses required clothing and posture, so it also stops before video and remains research-only. The documented next conditioning experiment is untested.

The [identity-first continuation](evaluation/identity-first/FINDINGS.md) tests reference ordering, depth conditioning and CPU registration of the original subject pixels. A new actual video retains defining appearance in conservatively31/33 frames, but remains a floating, truncated figure with unverified motion timing. It fails the frozen video criteria; three GPU calls are retained, two exploratory protocol deviations are disclosed, and no production promotion or unseen-test success is claimed.

Use one clear reference view with framing suited to the intended performance. Contact sheets can animate as multiple panels; tested headshots did not recover the source hand performance. Reference fitting and source framing are material limitations, not automatic subject tracking or pose reconstruction guarantees.

## Actual generation evidence

The [native motion integration](evaluation/native-motion-service/FINDINGS.md)
recovers the previously unscored independent-recording test:4/4 principal events,
33/33 recognizable reference-attribute frames, provisionally. The app's actual
upload/preparation/orchestration path repeats that result and is now deployed.
Raw/composite frames are identical under the full-frame mask; returned videos
match retained artifacts byte for byte. Fingers remain malformed, exact facial
likeness is not established, and normal-speed independent human/professional
review is outstanding. This is one recording and one fictional reference,
not population generalization or Genjutsu parity. Realistic object-swap quality
still fails. The earlier [diagnostic](evaluation/native-recipe/FINDINGS.md)
and all technical failures remain retained.

The studies below describe earlier decisions at their dates; the native release
above supersedes their former production-status statements.

The [reference-luma correction](evaluation/object-reference-luma/FINDINGS.md) reduces the raw target brightness mismatch while retaining green in17/17 frames and a0.96x area proxy. Full material/appearance quality still fails; diagnostic foreground annotations are not generic segmentation. The first missing-dependency failure is retained, and container preflight plus clearer render-error reporting are implemented.

The [object conditioning correction cycle](evaluation/object-reference/FINDINGS.md) rejects reference registration and a descriptive-prompt-only video. Registration loses green in17/17 frames; the descriptive prompt retains green but regresses scale to2.83x the source color-area proxy and adds a hole-like shape defect. Both raw/composited outputs and bounded replay commands are retained. The [source-luma follow-up](evaluation/object-luminance/FINDINGS.md) now produces green in17/17 frames at1.11x the source area proxy with accurate trajectory and passing numerical gates. Material/lighting remains below the frozen visual threshold; this actual video improvement is research-only.

The [object-mask oracle](evaluation/object-mask/FINDINGS.md) tests tighter
source-annotated masks with the model/reference/graph fixed. It loses the green
reference in17/17 frames, so it is rejected. Public licensed inputs, raw results
and a fresh-budget replay initializer are retained. Historical evaluator hooks
are explicitly kept on local legacy recipes rather than the new orchestrator.

The [precision and upstream-control diagnostic](evaluation/upstream-motion/FINDINGS.md) rejects both a BF16-only correction and pinned whole-body/hand/face preprocessing. Exact paired inputs isolate the precision contrast; both actual videos retain severe defects. GPU telemetry now works despite unavailable cgroup readings. These research paths remain outside production; no passing candidate or unseen verification is claimed.

The latest [explicit-motion experiment](evaluation/explicit-motion/FINDINGS.md) keeps the corrected reference fixed and tests a pinned Wan2.2-Animate model with CPU body/face controls. Its actual33-frame video regresses appearance and anatomy and matches only1/4 source events provisionally. It is rejected. The source, paired audit and retained failure are research evidence; the production model and realistic-quality limitation remain unchanged.

The [protected completion study](evaluation/protected-completion/FINDINGS.md) fixes the missing lower body in all33 frames of a new actual raw video while retaining the defining reference appearance. It still fails the frozen motion criterion at2/4 source events. One exploratory CPU-isolation amendment and all failures are disclosed; this research path is not promoted to production or claimed submission-ready.

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

Ten production tests cover workload bounds, masks, reference-latent trimming, rotation, input validation, target erasure and receipt retention without resubmission on a polling failure. One separately labeled experimental-reference test covers the rejected crop candidate. Live checks verified authorization, invalid workloads, signed job identifiers and real-upload inference. Browser QA verified motion generation and MP4/workflow/provenance downloads; a later clean checkout verified installation, build, local sign-in and authenticated backend status.

## Licensing and provenance

Original application code and procedural fixtures: **MIT**, see [LICENSE](LICENSE). Retain bundled third-party notices, including `webapp/build/sites-vite-plugin.LICENSE`. ComfyUI and all dependencies keep their own licenses.

- ComfyUI commit: `5cc4b870094c89090db54bd8d12649dcaf89f2ba`.
- [VACE weights](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged), revision `123acf1cc74bccbb9bfff8ac1ee72edc08c2341d`.
- [Wan Animate2 weights](https://huggingface.co/Comfy-Org/Wan-Animate-2), revision `e7181fe1896b7f2ce34120d1a3663413548240d7`.
- Model filenames are pinned in `model_config.py` and `motion_model_config.py`. No weights are bundled. Review upstream Apache-2.0 notices and component terms.
- Current native-motion model revisions, sizes and SHA256 are in `native_recipe_models.py`; pinned pose source/weights and Apache notices are in `vendor/wan_animate/provenance.json`. The converted checkpoint card declares Apache2; the generic conversion repository lacks a global license declaration. The adapter README attributes its Apache upstreams; this declaration gap remains disclosed. No converted weights are redistributed.
- PyTorch/CUDA and SDK versions are pinned. Upstream Comfy requirements are resolved at build; full dependency locking remains future work.

Built toward the [Comfy open-source challenge](https://comfy.org/open-source-higgsfield). This app uses the official SDK's documented self-hosted integration. Organizer acceptance and prize eligibility are not guaranteed. A public social post and formal entry submission are separate steps.
