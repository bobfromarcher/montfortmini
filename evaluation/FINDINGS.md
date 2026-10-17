# montfortmini validation — October 17, 2026

The two capabilities work on selected simple inputs, but the evidence does not
support general production readiness or Genjutsu parity. The strongest object
and arm-wave demonstrations survive controlled testing. Mirrored motion,
reference color without an explicit prompt, realistic driving footage, and
imprecise masks expose material failures. One confirmed preprocessing defect
was repaired and deployed: video display rotation now controls resize geometry
and mask mapping. Models, samplers, prompts and product features are unchanged.

## What was tested

Eight registered cases: development and held-out partitions each contain a
procedural object trajectory, illustrated arm motion, live-action object clip,
and live-action character-driving clip. Real holdouts come from different
original recordings; synthetic holdouts reuse the renderer with changed
direction, pose and appearance. Each run is 17 frames at 8fps, up to 480px.
Original recordings, submitted files, reference images, masks, exact float32
conditioning arrays, API graphs, all PNGs, videos, logs and hashes are retained.

Acceptance was written before tuning: reference/motion/stability scores >=3/4,
>=80% acceptable subject frames and no catastrophic collapse; controlled object
centroid error <=.10 frame diagonal and aligned character endpoint error <=.12;
composite outside-mask PNG pixels exactly unchanged; separate raw/encoded
background MAE <=3/255 and p95 <=10/255 outside an 8px boundary exclusion.
Technical output must decode to exactly 17 frames at the expected size/fps.
All 22 analyzed runs pass that technical gate. Visual scores are explicitly
**agent judgments**, with independent review pending.

Dataset/audit defects are retained rather than hidden. The first rotation
fixture lacked its intended display tag and its generation is excluded.
The real development mask misses part of the metal sphere; the held-out
bouncing target leaves its static mask. The gym crop is a burpee transition,
although the submitted prompt says jumping jacks. Sparse real annotations
were completed late: held-out labels preceded generated-frame inspection but
not inference. These are protocol deviations/confounds, so no clean aggregate
real-footage success rate or preregistered real-motion pass is reported.
See `EXPERIMENT-DECISIONS.md`, `fixture-correction.md` and `source-annotations.json`.

## Measurements and causal controls

| Test | Measured result | Interpretation |
|---|---|---|
| Development blue sphere, seed 42 | centroid error .00794 diagonal; 17/17 subject frames | Clear simple-case success with explicit color/shape prompt. |
| Held-out green sphere, reversed path | .00520 diagonal; 17/17 subject frames | Simple trajectory generalizes within the same renderer. |
| Development arm wave | endpoint diagnostic .0305 diagonal | Recognizable rising arm and reference appearance; modest lag. |
| Frozen driving frames | endpoint diagnostic .1465 | Arm stays largely lowered; temporal driving input contributes to movement. |
| Held-out mirrored/lowering arm | endpoint diagnostic .1613; duplicate/ghost arms | Fails motion/topology/stability despite preserved colors. |
| Disable target erasure | Blue cube remains instead of a sphere | Erasure enables shape replacement in this paired example. |
| Blue/green/gray references, identical default prompt and seed | Beige rounded forms versus a face-like patch; green absent | Reference influences output, but reference-only fidelity is unreliable. |
| Same seed 42 repeat | Raw RGB arrays exactly equal | Reproducible on this tested environment, not a universal guarantee. |
| Seed 123 | Raw-frame MAE 4.90/255 against seed 42; centroid error .00987 | Appearance changes with seed; simple motion still follows. |

Endpoint extraction is a disclosed synthetic skin/color heuristic; overlays are
provided. Duplicate arms make endpoint identity ambiguous. Color detection
can mistake blue shadows for the subject, and flow residuals can reward frozen
motion. These diagnostics do not replace the visual gates. `AGENT-REVIEW.md`
records stage-separated judgments and failure frames; `paired-analysis.json`
proves exactly which conditioning arrays were unchanged in each contrast.

Every tested object **composite PNG** has outside-mask maximum error **0**.
That preservation is caused by explicit compositing, not model fidelity.
On the held-out live-action object, raw background MAE/p95 are **5.01/20**,
failing the registered raw gate; composited MP4 is **1.86/6**, passing its
separate encoding gate. The output still fails target motion and scale.
Good background numbers cannot certify a successful replacement.

## The repair and its limits

FFmpeg independently displays the tagged source at 480x360. The old planner
used encoded 360x480 dimensions and prepared 352x480, stretching the displayed
image. The candidate reads display-matrix rotation, falling back to a legacy
tag, before sizing and mask placement; it prepares 480x352 with proportional
letterboxing. Nine tests pass, including an actually tagged video and known
red-region coverage. The backend was redeployed; its unauthenticated status
request still returns the expected 401.

The candidate was frozen before held-out output review. Three non-rotated
held-out clips produce **pixel-identical** raw outputs across profiles. On the
tagged held-out gym clip the candidate visibly follows the folded-to-standing
phase, whereas the baseline keeps an upright head and stretches arms downward.
Exploratory five-sample phase agreement is 5/5 versus 2/5, subject to the late
annotation/prompt confounds above. The geometry oracle and tests establish the
bug fix; that visual comparison alone does not isolate every generative change.

A separate development pair expands the mask to cover the complete metal
sphere. The baseline still produces an elongated capsule; the candidate
produces a round blue disk. Reference shading remains poor. The registered
undercoverage case remains a failure. Correct geometry does not solve mask
tracking, realistic lighting, occlusion, ghost limbs or background contamination.
The walking case retains severe background ghosting at frames 14–16.

## Provenance, resources and spending

Comfy commit `5cc4b870094c89090db54bd8d12649dcaf89f2ba`; official SDK 0.5.0 /
proxy 0.1.6. VACE uses the Comfy-Org repack revision
`123acf1cc74bccbb9bfff8ac1ee72edc08c2341d`, 1.3B fp16, 20 steps, cfg 5,
uni_pc/simple. Motion uses Wan-Animate-2 revision
`e7181fe1896b7f2ce34120d1a3663413548240d7`, distilled int8 convrot,
10 steps, cfg 1, lcm/simple. Motion conditioning is the raw RGB source encoded
by the native node, plus reference conditioning; there is no separate pose
extractor. Actual SHA256 of all five shared/model files matches pinned registry
LFS hashes. See `model-integrity.json`, per-run graphs/package freezes and
`candidate-freeze.json`; only production `media_pipeline.py` changed.

There were **23 successful generations**, including the rejected fixture,
plus one initialization failure before sampling: 24 attempts. Measured worker
time totals **1,313.17s (21.89 minutes)**; analyzed runs account for 1,273.79s.
Object runs span 29.71–60.00s (median 46.74); motion 61.49–139.56s (median 75.72).
One-Hz GPU sampling observed a peak **27,287 MiB** VRAM on L40S. Allocation was
2 CPU / 32 GiB RAM; CPU/RAM peaks were not sampled. A separate CPU model-file
hash audit took 43.88s. Worker timings exclude some image/allocation overhead
and are not exact billed GPU seconds. No warm GPU containers, volumes, or
automatic inference retries were used.

Observed Modal summary usage/credits rose **$0.34 → $1.22**, an **$0.88**
increase; the ephemeral-app breakdown rose $0.30 → $1.24, or $0.94. The UI
totals do not reconcile and may lag, so neither is a settled per-run bill.
**Cash spend remained $0.00**, with the net spend limit at $0 and $30 monthly
included credits. Screenshots, timestamp and exact UI observations are in
`billing.json` and `billing-start.jpg` / `billing-end.jpg`. No paid Genjutsu
generation or model substitution was purchased.

## External comparison and independent assessment

No verified matched Genjutsu pair was obtained: the free prepared submission
had no confirmed tool receipt; the human-queued job used different inputs and
is excluded. `GENJUTSU.md` separates UI observations from unproven server-model
hypotheses. Nothing here establishes how Higgsfield implements Genjutsu.

[Ref2VA-VSA](https://github.com/Kablex/ComfyUI-Ref2VA-VSA) was assessed against
observed ghost arms/background leakage. It patches H3 attention, not these Wan
graphs, and its example does not provide an equivalent driving/mask test.
The [H3 model license](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
excludes this US deployment; Apache-licensed node code does not override that.
No H3 weights were downloaded or run, and no speed/quality benefit is claimed.
The detailed compatibility and isolated-test assessment is included.

The offline `blind-review/index.html` presents neutral shuffled samples with
reference, source, raw and composite videos; `review.csv` is blank and the key
is separate. Another professional can inspect all frames, score the registered
rubric, recompute CSV/JSON diagnostics without GPU spending, verify SHA256
provenance, or replay the 22-row experiment matrix. Full original footage and
CC attribution accompany the evidence; code licensing does not relicense it.
No outside professional has yet scored this packet. Tiny single-case cells,
one main seed, short 8fps clips, reused synthetic renderer, and cross-domain
illustrated references limit all generalization claims.
