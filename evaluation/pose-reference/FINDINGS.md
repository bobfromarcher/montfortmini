# Pose-only reference preparation — 2026-10-18

**Result: rejected. No passing new video, no production deployment and no
submission-readiness claim.** This is a new tested alternative to the failed
Klein→Qwen reference cascade, not another seed or resolution reroll.

## Implemented and observed

The alternative removes Klein and extracts source body geometry on CPU with
MediaPipe Pose Landmarker Full0.10.35. It maps33 detector landmarks to an18-joint
colored skeleton, omits invisible/out-of-frame joints, and sends that guide plus
the original-detail identity into the existing native Qwen-Image-Edit-2511
40-step/seed42 recipe through the official Comfy SDK. The Qwen-family authors
document keypoint-map editing support; success on this case was unproven.
The video path retains the previously frozen Animate2 graph and original RGB
driving footage. It was not reached. All14 frozen source hashes match.

The result retained curls, beard and plausible two-lens glasses. It **lost the
blue blazer/ivory shirt**, changed the head direction, and moved a hand behind
the body. It fails the predeclared reference gate. These observations are agent
assessments. No claim of independent identity verification is made. The failure
occurs before animation. One rendered still cannot establish video fidelity,
motion timing, temporal stability, anatomy throughout a clip or background
preservation. All old outputs and this new failure remain available privately.

Removing source-person RGB did not suffice to preserve clothing and source pose
jointly. That is the demonstrated limit of this tested recipe on this case.
The guide drops depth, detailed fingers and exact3D orientation; whether this
loss caused the orientation/hand failure is a hypothesis. Input ordering,
prompt interpretation, quantization and model capacity were not isolated.
No universal ceiling or Genjutsu-internals claim follows.

The protocol allowed a matched RGB-guide control only after a reference pass,
then a development video, then one genuinely new licensed recording. The first
gate failed, so none of those jobs ran. Compared with historical failures,
both prompt and preparation changed; this is a complete-candidate comparison,
not a one-factor causal result. The old signer remains development material.
Four source-only development motion landmarks were frozen before any candidate
video; they are not independent-held-out evidence or a retrospective prior pass.

## Verification and resources

Two new CPU tests cover anatomical joint convention and omission of invisible/
out-of-frame joints. All15 current production/detail/pose tests passed. The
offline audit passed original/guide/identity hashes, confirmed SDK receipt,
native seed, direct-original identity pixels and root/stage output consistency.
Guide conditioning is944x1104; identity conditioning672x1024. Production files
and earlier video graph are unchanged. The first CPU preflight caught a missing
module mount before GPU dispatch; it was fixed and refrozen before this trial.
No technical GPU retry occurred. Full independent GPU reproduction/professional
review remain outstanding; no clean-machine or new full-video pass is claimed.

Declared cap:$4 additional included credits,4GPU calls/3000worker seconds,
with2calls/1560seconds reserved for video and independent verification. Actual:
1GPU call,388.599worker seconds. L40S sampled peak VRAM is recorded in
resource-summary.json;64GiB allocation is not a measured physical RAM peak.
Modal displayed$6.17→$6.45usage and$23.83→$23.55remaining, cash$0/spend cap$0.
The$0.28delta is an asynchronous account reading, not an exact per-job invoice;
the disagreeing animated breakdown and CPU preflight overhead are retained.
Final container inventory is empty. No additional inference after the gate fail.

The pose model card explicitly lists Apache2.0 (page2). Exact9,398,198-byte
model SHA256 is4eaa5eb7a98365221087693fcc286334cf0858e2eb6e15b506aa4a7ecdcec4ad.
Generator/video weight revisions remain the already verified Apache2.0 assets.
No closed generation API or new generator model was used. Human source and its
derivatives stay private because promotional likeness permission is unresolved.

## Executable commands

```sh
# Optional separate Python3.11 CPU environment:
python -m pip install -r evaluation/requirements-pose.txt
# Obtain official task bundle at the recorded URL; verify the SHA256 above.
python pose_guide.py --source SOURCE_FRAME.png --model pose_landmarker_full.task --output NEW_GUIDE_DIRECTORY
# Offline checks, with evaluation requirements installed:
python -m unittest discover -s tests -v
python evaluation/audit_pose_reference.py --run /evidence/keypoint-anchor --output audit.json
```

Remote entrypoint:`python -m modal run pose_reference_candidate.py --help`.
Replay requires authorized compute, the saved budget directory, original inputs,
the frozen code/model assets and explicit observed credit thresholds. The saved
ledger blocks automatic reuse after reserved/failed attempts. No automatic
retry. Optional video/fresh-source wrappers remain unexercised in this study.

## Specific next technical change and unresolved resources

The next warranted experiment is **identity-first editing with explicit body
orientation geometry**: original character as the primary image, source pose
as a separate guide, and a source-body depth/normal guide that encodes torso
orientation without source clothing texture. Test input-role ordering first in
a paired comparison before adding a depth dependency, rather than changing
models and conditioning simultaneously. This is a hypothesis, not a solved or
tested implementation. It was not run after this protocol's stop.

Depth-Anything-V2-Small is an Apache2.0 source for a potential depth guide, but
would require compatibility and geometry checks. InstantX's Apache2.0 Qwen
ControlNet Union documents depth/pose control for base Qwen-Image; its card does
not establish a drop-in identity-preserving2511 edit adapter. It was not
installed or downloaded. A compatible trained spatial-control/identity path
must be established before promising that stronger conditioning fixes this.

No GPU-memory or credit shortage occurred. A further bounded conditioning
experiment could use remaining included credits; buying a larger GPU is not
supported by this evidence. The need for training or additional paid compute
has not been demonstrated. Existing real object scale/lighting failures also
remain unresolved. The realistic quality target is still unmet.

Primary sources:
- https://github.com/QwenLM/Qwen-Image/blob/main/Qwen-Image-Edit-2509.md
- https://huggingface.co/Qwen/Qwen-Image-Edit-2511
- https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/index
- https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf
- https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf
- https://huggingface.co/InstantX/Qwen-Image-ControlNet-Union
