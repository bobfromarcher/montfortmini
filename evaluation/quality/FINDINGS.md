# montfortmini quality findings — October 17, 2026

**The realistic reference-fidelity and full-performance motion target remains
unmet.** Simple object and illustrated-motion examples work; the new realistic
cases expose scale/lighting and pose-transfer failures. No Genjutsu parity or
prize claim is supported. We keep the existing two features and sampling graphs.

## Decisions and evidence

The first eight development runs isolate reference selection, target caption,
separate driving caption, resolution, reference fitting, and full-body framing.
The whole multi-view sheet is animated as panels/multiple people. Selecting a
single portrait improves one-face resemblance. Center-cover removes artificial
gray reference bands in both a high-resolution contrast and the actual default
prompt/480px-long-side contrast; source/mask tensors and graph are unchanged in
the latter. Detailed captions and higher resolution alone do not restore hands
or the source setting. Full-body selection restores more arm movement but does
not turn the standing reference into the seated source performance.

The previously viewed walking stress case loses its severe late background
ghosting under cover fitting, but still fails rear-facing gait. The prospective
push-up pair remains upright under both profiles, and cover fitting crops feet
and shifts framing. We therefore **reject center-cover as a global default**,
restore the exact rotation-corrected production preparation, and retain the
candidate/outputs as research evidence. Input preparation is influential, but
this does not establish an architectural impossibility or a universal solution.

The shipped repair addresses an observed execution failure: a 30s SDK HTTP
status read timed out after a confirmed submission. The bridge now submits once,
saves the job receipt immediately, and waits with an HTTP timeout bounded by
min(120s, the job timeout). No generation retry is added. Five later prospective
generations completed with that bridge. Future evaluator failures retain the
graph, inputs, logs and any receipt. The original failed platform trace is kept.
Its Comfy job ID/internal log/output were not returned by the old bridge; this
is an explicit provenance gap.

## Prospective cases

Inputs, annotations, rubric and candidate were frozen before generated-test
inspection. Two original synthetic sequences and two different real recordings
were added. Old holdouts, private temporal crops and mirrors are not new holdouts.
The static 52s push-up selection was rejected during source-only inspection and
replaced by the moving 71..73.125s interval before inference; both are retained.

| Case | Result |
|---|---|
| New vertical object path | Agent visual pass; green sphere in 17/17 frames; centroid error **.00838** frame diagonal. Raw outside-region MAE/p95 **.75/2**; finished PNG outside-mask max error **0**. |
| New bee/ball recording | **Fail:** replacement too large and lighting mismatched, despite 17/17 green detections, centroid error **.05060**, raw preservation **1.96/7**, encoded preservation **1.77/4**, and finished PNG max error **0** outside mask. Exploratory target/source area ratio **2.53×** supports the scale observation. |
| New two-arm sequence | Agent visual pass; recognizable rise/lower timing and no observed duplicate limb. Exploratory skin-extrema endpoint error **.03838** diagonal over 34/34 points; inspect overlays. |
| New push-up recording | **Fail, both profiles:** no horizontal push-up. The candidate adds framing/cropping problems. |

Every completed run passes technical size/frame/fps checks: 17 frames at 8fps.
Motion masks cover the full frame; outside-edit preservation is not applicable.
Object finished-background equality is explicit compositing, not proof of model
preservation. Agent scores in AGENT-REVIEW.csv are not independent judgments.
Coarse lens counts cannot certify biometric identity or fine eyewear accuracy.
The two-hand heuristic was implemented after output inspection and is exploratory;
it cannot replace the frozen visual gates. No population success rate is inferred.

Only the push-up has a newly executed baseline/candidate pair. Object preparation
was unchanged, and the new synthetic motion reference is aspect-matched: saved
reference pixels are byte-identical under both recipes. That is an input-identity
control, not an unexecuted paired inference. Model graphs/revisions are unchanged.

## Provenance, comparator and resources

Actual inference: app/service → official comfy-sdk 0.5.0 → comfy-api-proxy 0.1.6
on loopback → pinned ComfyUI → VACE 1.3B or Wan Animate2 distilled int8. Comfy
commit 5cc4b870094c89090db54bd8d12649dcaf89f2ba; VACE revision
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d; Animate revision
e7181fe1896b7f2ce34120d1a3663413548240d7. Exact graphs, masks, conditioning,
original bytes, all output frames, environments, logs and hashes are retained.
Earlier actual model-file hash audit remains in phase 1. Early phase-2 runtime
metadata did not hash every harness/SDK source; frozen modules, executed graphs,
versions and later source hashes disclose that provenance limit.

The two proposed VAE files have matching headers and full payloads for all 194
tensors; their file metadata differs. A VAE substitution is not justified. The
official distilled Comfy template supports the existing LCM/simple 10-step
sampler. Ref2VA-VSA remains unrun: reviewed H3 licensing/US deployment and Wan
compatibility constraints are documented in docs/ref2va-vsa-evaluation.md.

The private Genjutsu source/reference/output files were recovered after phase 1.
They are useful observable comparison media, but seed, backend and internal
settings are unknown; our later reference crops and shorter/lower-fps outputs
also differ. No fair statistical superiority or backend-reconstruction claim is
made. Original private assets and derivatives are excluded from public media.

Phase 2: **14 successful generations**, one recorded polling failure, and one
reserved Modal runner failure: **16 budgeted attempts, then stop**. Successful
worker time **1279.12s (21.32 min)**;
failed client time **65.12s**, with extra platform overhead unmeasured.
Peak 1Hz sampled VRAM **28,862 MiB** on L40S;
2 CPU / 32 GiB allocated. Summed process-tree RSS peaks at
56,763 MiB, double-counting shared pages;
it is not physical RAM consumption. The separate VAE CPU audit took
11.72s. Timings do not establish a speedup.
Observed rounded credit usage rose **$1.22 → $2.23 (~$1.01)**; **cash $0** and
the net-spend cap stayed **$0**. Billing summary/breakdown differ and may lag;
this is not a settled per-run invoice. No additional GPU tests are scheduled.

## Reproduction and entry status

A separate clean checkout installed 686 frontend packages, passed TypeScript
checking/build, and served the two-mode interface. The final production Python
files passed 10 tests in a new venv; one experimental-reference test also passes.
Local sign-in requires cookies. Vinext development needs the documented backend
settings in .env.local; .dev.vars supplies Worker preview. HTTP page and
authenticated backend status returned 200 after this documented configuration.
No full GPU Docker build/inference was possible on the 4GB laptop. No independent
professional has scored the review packet or independently reproduced inference.

The 108-second captioned demo shows actual original procedural outputs, a
retained failure, the clean interface, and the real SDK path. No frame repair,
interpolation, private likeness or Genjutsu output is included. Public review
media uses original art plus attributed CC-BY bee footage. The government
exercise recording is retained for private research, not public demo/media
clearance. Demo/social draft/form text/checklist are prepared. Social publication,
registration verification, formal submission and organizer acceptance remain
separate outstanding steps; no submission receipt or award is claimed.
