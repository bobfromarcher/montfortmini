# montfortmini — entry materials

Status: prepared experimental entry; not formally submitted. Realistic quality
target remains unmet. No award or organizer acceptance is claimed.

Current October19 update: [native motion](../evaluation/native-motion-service/FINDINGS.md)
is integrated and deployed after a successful independent-recording recovery and
app-path regression. Frame ratings remain provisional; fingers are malformed,
exact likeness is not established, and realistic object quality still fails.
The public108-second demo predates this update and needs refreshed cleared media.
The new [object conditioning cycle](../evaluation/object-reference/FINDINGS.md) rejects both reference registration and a descriptive prompt; scale/shape remain inadequate. The [source-luma combination](../evaluation/object-luminance/FINDINGS.md) improves object color/scale/trajectory, but still fails the visual lighting/material gate and remains research-only. The [reference-luma correction](../evaluation/object-reference-luma/FINDINGS.md) further improves shade but remains below the material gate. Error-reporting fixes are deployed; generative settings remain experimental. Earlier diagnostics below remain retained historical decisions.

October19:[precision and upstream-control comparisons](../evaluation/upstream-motion/FINDINGS.md)
both fail the visual gate. No candidate promotion or unseen verification follows.

Latest [explicit-motion experiment](../evaluation/explicit-motion/FINDINGS.md)
completed an actual33-frame paired video with the corrected reference fixed.
It regresses appearance/anatomy and fails motion. The candidate is rejected;
the existing production workflows and108-second cleared demo remain unchanged.

**Repository:** https://github.com/bobfromarcher/montfortmini/tree/codex/validation

**Review:** https://github.com/bobfromarcher/montfortmini/pull/1

**Demo:** `montfortmini-demo.mp4`, updated October18,108 seconds,2592 decoded frames, captioned, no soundtrack. It includes the frozen synthetic regression and reports the failed fresh identity test; human research footage is excluded.
Public repository path after publication:
https://github.com/bobfromarcher/montfortmini/blob/codex/validation/submission/montfortmini-demo.mp4

**Suggested description:**

montfortmini is an independent open-source workbench for reference-guided
object replacement and character motion transfer. It runs pinned VACE 1.3B and
native Wan2.2-Animate workflows through the official Comfy SDK and a self-hosted Comfy
API proxy. Users upload a short clip and reference, draw a manual edit region
for object replacement, and download MP4, the executed workflow and run details.
The MIT repository includes setup instructions, original demonstrations,
evaluation commands and retained failures. Simple illustrated/object examples
work; realistic pose, identity, scale and lighting remain inconsistent. The demo
shows actual outputs and a failure rather than claiming Genjutsu parity.

**Models/tools:** ComfyUI; official comfy-sdk 0.5.0 and comfy-api-proxy 0.1.6;
Wan2.1 VACE1.3B and native Wan2.2-Animate14B with pinned converted weights,
Lightx2v acceleration/relighting adapters and ViTPose133 controls; FFmpeg/Pillow/NumPy/OpenCV
for preparation/evaluation; Modal L40S; React/Vinext frontend and private Sites
hosting. No Higgsfield backend or closed generation API is used.

**Categories:** Best Overall consideration follows the published rules.
Open Weights Only appears relevant because inference uses open weights without
partner-generation APIs; organizers make that determination. No LTX/FLUX/H3
bonus is claimed because those are not core inference models here.

**Local setup:** follow the repository README. GPU inference requires sufficient
hardware or the entrant's own included/authorized cloud credits. The fully local
GPU Docker path is documented but not independently executed on this laptop.

**Try link:** an owner-private deployment exists, but anonymous/judge access is
not established. Do not present it as an anonymously accessible demo. The
published rules make a hosted link optional; repository/demo are the review path.

**Still needed from the entrant:** verify registration, publish the prepared
social demo post and retain its URL, review all submitted representations and
terms, submit through the official form, and retain the receipt. Submitter name,
email and a social-post URL have not been invented or prefilled.

Official registration: https://form.typeform.com/to/Ayn9Cwfj
Official submission: https://form.typeform.com/to/V1dSQrkS
Rules: https://comfy.org/open-source-higgsfield

**Recovery validation:** `evaluation/RECOVERY.md` documents the rejected Klein→Qwen→Animate2 candidate, eight final-phase GPU attempts, the unchanged production path, a new independent-recording identity failure, retained regressions and reproducible offline audits. The realistic quality target remains unmet.
