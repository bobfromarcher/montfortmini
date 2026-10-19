# Explicit motion control experiment

Frozen before the first generated video. Private development evidence, not a
Genjutsu backend identification or an independent held-out test.

The retained protected-reference control completed the lower body in33/33 raw
frames but matched only2/4 source events. This supports testing motion control
instead of another reference-image variant. Hold the actual source, full mask,
reference tensors, seed42,480×560 geometry and33 frames at8fps fixed.

Candidate: native Comfy `WanAnimateToVideo`, Wan2.2-Animate14B BF16,
Comfy repack revision ee6f4a40737a995bf5818954cfce6d59443b0f04, SHA256
7d37cb0120488dec2a061135aa3018426925318a60838c3de935c829abc88667.
Model repository and upstream code declare Apache2.0. Reuse the already pinned
Wan2.1 VAE,T5 and CLIP-VisionH. No acceleration or relighting LoRA.
Upstream code revision1ea34ff48f87168174e12956e200b1d908b1c5ff specifies
20 steps,CFG1,shift5 and DPM++; Comfy dpmpp_2m/simple is comparable, not a
bit-identical upstream sampler. Keep the prior appearance prompt fixed.

CPU source preparation uses MediaPipe0.10.35 FullPose,VIDEO mode,one pose,
threshold.5,125ms frame intervals. Render mapped OpenPose18 body skeletons;
no invented invisible joints, temporal smoothing, retargeting, hand meshes or
face meshes. Source face landmarks define a square256px RGB crop; the native
node resizes this to512px. The controls were checked at the four frozen event
frames. This is an approximate independently implemented preprocessor, not
the official DWPose133 pipeline. Low-light face input and absent finger detail
are known limitations. Face-control pixels may leak source identity.

This deliberately changes the model/control/solver bundle. The paired inputs
test whether that bundle improves the demonstrated failure; they cannot
attribute any gain solely to the backbone or a particular control branch.

Use the unchanged visual rubric inRUBRIC.md and stricter existing event gate:
The inherited rubric's historical phase budget is superseded by budget.json
and the smaller hard limit below;its visual acceptance thresholds are unchanged.
all applicable dimensions>=3/4,at least28/33 clear reference-attribute frames,
at least3/4 source events matched within±2frames. Frozen events:8 cross-torso,
16 shoulder/waist,24 hands down,28 hand at mouth. Any duplicate major limb,
extra subject,collapse or major truncation fails. Inspect all33 raw frames;
score composited result separately. A full motion mask means explicit
compositing does not repair the video or demonstrate background preservation.
Ordinal agent scoring is provisional; independent professional review remains
necessary. No population success-rate or identity-biometric claim.

Hard limit: $3 additional included credits,3 GPU calls,2700 reserved worker
seconds,900s per call,automatic retries0. Baseline displayed usage$7.59 and
remaining$22.41,stop at usage$10.59/remaining$19.41 or any cash charge/cap change.
The account cash cap remains$0. CPU image preparation is included in the same
credit delta; worker ceilings are conservative reservations,not measured cost.

One development video. If motion fails,stop. Only if motion passes and a
specific source-identity leak is demonstrated may one matched face-off ablation
run; its only graph change is removal of `face_video`. Otherwise no reroll.
Reserve one900s call for a frozen passing candidate on genuinely independent
footage. Do not call a new crop,mirror or previously tuned recording unseen.
Any GPU technical failure stops this cycle. A pre-GPU packaging failure may be
fixed before code is refrozen and any GPU call is dispatched.

If all development gates pass,freeze the selected graph,code,controls and
reference policy before selecting/executing prospective verification. Retain
every outcome and regression. No promotion,parity claim or submission on a fail.
