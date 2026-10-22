# Precision and upstream-control diagnostic

Keep model revision,reference/source/mask tensors,seed42,480×560,33frames,
8fps,prompt,sampler20/dpmpp_2m/simple,CFG1 and shift5 fixed.

1. Compare the rejected explicit-motion run with an identical graph and controls,
   changing only Comfy startup to `--bf16-unet`. Confirm executed dtype in logs.
2. Only if precision alone fails the frozen visual gate,compare that result with
   official pinned ViTPose133 controls at the same BF16 setting. This changes the
   control preparation bundle:whole-body/hand landmarks,upstream v2 renderer,
   official face-landmark crop and512px OpenCV-linear resize. The already cropped,
   single-person source uses the upstream supported detector=None mode. No YOLO
   detector,retargeting,FLUX preparation,model switch or seed search.
3. Only after a development pass,freeze the candidate and test a genuinely
   independent recording under its own source-only input freeze.

Same visual acceptance:all applicable dimensions>=3/4,>=28/33 clearly retained
reference attributes,>=3/4 frozen source events within±2frames,no duplicated
major parts/collapse. Events remain8 cross-torso,16 shoulder/waist,24 hands down,
28 hand at mouth. Raw and composite reviewed separately;full-mask arrays must
remain identical. Agent ratings are provisional,not independent professional
review. No previously tuned source can count as unseen.

Hard cap:$2 additional included credits;3 GPU calls maximum,900s each;third call
reserved for verification. CPU whole-body preparation is limited to900s plus
image construction within the same credit delta. Baseline displayed7.72usage /
22.28remaining;stop9.72usage /20.28remaining or any cash charge/cap change.
Any GPU technical failure stops. First quality failure permits only the already
specified whole-body contrast;second failure ends the cycle. No rerolls or
post-output amendments. Earlier stopped ledgers stay unchanged.

Wan upstream code1ea34ff48f87168174e12956e200b1d908b1c5ff and the pose weights
Wan-AI/Wan2.2-Animate-14B atcb93a225fbaf1ca100f54e79da8f994995b689b3 declare
Apache2.0. All394 ONNX/external-data files totaling2,549,362,899bytes are pinned
and hashed;vendor/wan_animate/provenance.json preserves per-file provenance and
LICENSE. Existing diffusion model remains the Comfy repack pinned previously.
