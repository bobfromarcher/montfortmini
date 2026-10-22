# Adversarial review — one bounded cycle

P0, demonstrated: the realistic quality target fails before animation. The fresh
signer lost glasses/curls/face; later video0/33glasses vs28required. The default
app still has the older reference preparation and no validated general fix.
No README, metric or cinematic teaser can turn that into a successful entry.

P1, demonstrated implementation/input defect: both image helpers cap identity
at512pixels, discarding detail that native Qwen VAE conditioning could receive.
Pinned nodes_qwen.py expands each reference to about1MP. Correction directly
resamples original identity pixels to a larger bounded canvas, keeping legacy
aspect and Qwen vision/VAE token geometry constant. Model/seed/prompt unchanged.
Hypothesis: this improves defining face/accessory retention; not yet proven.

P1, demonstrated experimental weakness: previous full_reference_resolution=True
used nearest-neighbor enlargement after loss. It changed canvas/token geometry,
but introduced no actual original high-frequency detail. The earlier conclusion
must be limited to that tested operation, not genuine high-detail conditioning.
New controlled high-frequency CPU test exposes the lost signal; native-condition
geometry and source/reference provenance will be audited in the paired GPU test.

P1, demonstrated evaluation gap: four fully timestamped motion landmarks were
not frozen in the previous real test. Do not claim its formal3/4 timing gate.
Only a passing development video justifies selecting/freezing a new recording's
source-only landmarks and running the final independent test in this cycle.
No old signer, mirrored clip or temporal crop can become independent again.

P1, retained separate quality blocker: real object replacement has scale/lighting
failures despite exact outside-mask compositing. No object-model changes are
justified by the identity-input hypothesis. Its code/graphs and recorded success
and failure remain unchanged. Raw output quality and composite preservation stay
separate; successful compositing does not establish realistic insertion.

P2, submission readiness: official SDK/self-hosted proxy is really executed;
public code/license/local instructions and108sec demo exist. Registration,
social-post publication, formal submission and independent professional/GPU
review remain unverified/pending. A draft PR and honest negative result are
reviewable work, not proof of competitive quality or organizer acceptance.

Action: correct the original-pixel loss with existing models only. Execute the
registered image gate, one placement ablation if needed, then at most one video
and one new-source test if prior gates pass. Stop at budget/quality failure.
No new branding, features, speculative dependencies or model switching.

Official rules rechecked2026-10-18: https://comfy.org/open-source-higgsfield
Pinned implementation evidence:
https://github.com/Comfy-Org/ComfyUI/blob/5cc4b870094c89090db54bd8d12649dcaf89f2ba/comfy_extras/nodes_qwen.py#L68
