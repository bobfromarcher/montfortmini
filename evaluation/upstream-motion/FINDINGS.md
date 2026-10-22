# Precision and upstream-control diagnostic: both rejected

The quality target remains unmet. Two planned paired videos completed;neither
is promoted. GPU work stopped before the reserved verification call. No unseen
footage,independent reproduction,professional review or competition entry is
claimed.

| Contrast | Controlled evidence | Result |
|---|---|---|
| FP16 → BF16 diffusion precision | Graph and all five conditioning tensors exactly equal;logs confirm bfloat16 | Same head extrusion and blurred face/hands at frozen event frames. Mean raw pixel MAE versus FP16 is1.046/255;precision alone is not an adequate correction. |
| Approximate body controls → upstream whole-body controls | Graph,model,source/mask/reference,seed,sampling and BF16 unchanged | New headwear absent from reference,large protrusions and blurred anatomy. Rejected at the same four native event frames. |

Early rejection is based on clear hard-gate defects atframes8,16,24,28. No
full33-frame subjective pass rate or complete motion score is invented. Both
videos decode33frames,480×560,8fps. Whole-body raw/composite PNG pixels match
exactly;full-mask compositing does not repair the failure.

The second contrast changes a control bundle:ViTPose133 landmarks including
hands,official v2 rendering,face-landmark crop and OpenCV-linear512px resize.
It does not isolate each subcomponent. Already cropped single-person input
uses the upstream supported detector=None mode. No detector,FLUX preparation,
retargeting,model switch or seed search is added. The original CPU face resize
was corrected from bicubic to upstream linear before any new GPU output;the
original archive and correction record remain. One pre-GPU Modal preflight
wiring failure was repaired and refrozen without dispatching a GPU.

This narrows the diagnosis:executed precision and the missing upstream hand
controls are not individually sufficient explanations/solutions. The experiment
does **not** prove checkpoint incapacity,hardware shortage or the identity of
Genjutsu's backend. A known-good end-to-end upstream sampling reproduction is
still missing. The captured native template uses different converted weights,
an acceleration adapter and6-step Euler/shift8 sampling;our base20-step
DPM++/shift5 approximation is not its reproduction. Exact differences are in
official-template-differences.json. That is the next prerequisite before more tuning or model
switching;sampler/runtime compatibility and source-face appearance leakage
remain hypotheses requiring isolation.

Measured GPU workers:135.376586488s and123.794094168s,total259.170680656s.
L40S,2CPU,64GiB allocation. Sampled peak VRAM44,382MiB and44,217MiB from131/120
samples. The repaired logger now retains GPU rows while explicitly recording
missing cgroup-memory readings;this correction is verified in actual GPU runs.
Both jobs used the official SDK;graphs,receipts,environments,logs and controls
are retained. No OOM or generation exception occurred. See resources.json,
decode.json and the two paired-audit JSONs for measurements.

Budget:$2 included credits,at most3 GPU calls/2700 reserved worker seconds,
with one verification call reserved. Only2 GPU calls/1800 ceilings were used.
CPU whole-body preparation took the exact time in controls-freeze.json.
Final displayed account charges remain$0 with a$0 cash cap;billing.json records
rounded asynchronous usage/balance observations,not an isolated invoice.

Pinned code:Wan1ea34ff48f87168174e12956e200b1d908b1c5ff. Pose weights:
Wan-AI/Wan2.2-Animate-14B@cb93a225fbaf1ca100f54e79da8f994995b689b3;
394 files/2,549,362,899bytes verified individually. Apache2 vendor LICENSE and
provenance remain alongside unchanged upstream source and the extracted crop
function. Existing pinned Comfy/model/SDK versions are unchanged. The new
diffusion precision is explicitly requested with --bf16-unet;production retains
the default auto setting.

Run CPU preparation with upstream_motion_candidate.py --kind controls,then
the frozen precision and conditional wholebody stages. Use --help for arguments.
Never erase a stopped ledger or create a false candidate-pass.json to replay.
Source,mask and reference pairing can be checked directly in conditioning.npz;
review raw output separately from composite. Human frames,face controls and
landmarks stay private. Public metadata omits those pixels. Existing realistic
object scale/lighting failure remains unresolved. Current status:research
diagnostic complete;quality and submission readiness **failed**.
