# montfortmini v0.1.0-alpha.1 — developer preview candidate

Draft release notes. No version tag or public alpha release is claimed here.

montfortmini is an open-source workbench for short reference-guided object
replacement and character motion transfer. It runs ComfyUI workflows through
the official Comfy SDK. Technical users provide their own compatible GPU or
Modal account and backend credentials; the maintainer's hosted studio remains
private.

This candidate includes the native Wan2.2-Animate motion path, whole-body/hand
pose and face controls, VACE object replacement, raw/finished comparisons,
workflow exports, pinned model provenance and retained evaluations. The next
quality priority is facial and replacement identity consistency.

What the evidence supports: the actual app path completed short motion clips
with recognizable broad reference attributes and source movement in provisional
frame review. Simple synthetic object examples run. What remains inadequate:
exact face/glasses proportions, hands, broader motion generalization, realistic
object appearance/materials, occlusion and consistency across shots. There is
no demonstrated Genjutsu parity or superiority.

Start with the candidate branch's README. Measured native cloud allocation:
L40S48GB/64GB requested host memory,480x560/33frames/8fps. This is not a minimum
hardware specification. The local Docker GPU route is documented but not
independently reproduced; smaller hardware may require changes. Source setup,
current frontend checks and the61-test CPU suite do not certify video quality.

The existing108-second demo is archival and shows earlier recipes. A current
cleared native-motion sample, fresh-user setup verification, exact release
commit and final checks are still needed before calling this a verified
public-alpha video release. Private human-source research media is excluded.

Code is MIT; upstream components/models and CC BY sample media retain their
own terms and notices. Model weights are downloaded, not redistributed.
No paid account is provided, no automatic generation retries are configured,
and temporary results must be downloaded.

Feedback that helps: source commit, hardware/runtime, recipe and seed, which
reference feature changed, when it changed, and cleared source/reference/raw
output if you can share them. Mark pose/visibility uncertainty. File setup
failures separately from identity/motion failures; remove credentials before
sharing logs.
