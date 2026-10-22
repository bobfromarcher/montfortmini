# One review/correction/verification cycle

Baseline: public source commitb05422b, previous failed recordings/outputs retained.
No production deployment yet. Cash cap0; included-credit/time/call limits in
budget.json were declared before GPU inference. Stop without increasing them.

Demonstrated defect: both identity helpers reduce large original inputs to512px;
the pinned Qwen Edit Plus node expands them to about1MP before VAE encoding.
Earlier high-resolution control used nearest-neighbor enlargement AFTER loss.
That control cannot rule out the benefit of actual original detail. No claim
that detail alone explains the entire face/headwrap/style failure.

Correction uses original pixels directly on an integer multiple of the legacy
identity canvas, bounded by1MP and available original pixel count. For the
1024x1536 fictional portrait,336x512 becomes672x1024. The legacy aspect and
native Qwen reference token geometry stay fixed. Low-resolution original art
and the511x477 private portrait retain pixel-identical input preparation.

First experiment changes Qwen identity pixels only, using the exact retained
Klein source frame. Original bytes/graph/prompt/seed42/models remain fixed.
If reference fidelity still fails, one predeclared placement ablation applies
the same policy to Klein and Qwen from the original source frame. No further
prompt/weight/sampler changes. If neither reference passes, stop inference.

Reference gate: original defining glasses, salt-and-pepper curls/beard and face
must be recognizable; blue blazer/ivory shirt must remain; source posture and
framing plausible, no invented props/extra subject. Reject source headwrap
persistence or cartoon identity. A still-image pass only permits video testing.

Video gate: frozen previous anchored rubric, all applicable dimensions>=3/4,
at least28/33frames with defining reference attributes, no collapsed/duplicate
limbs or extra subject, recognizable source gestures in order. Raw/composite
separate; full-mask pixel equality is not background preservation. Agent scoring
is provisional; professional scoring remains outstanding.

Only a passing development video permits one new independently recorded licensed
source test. Select/crop/annotate source-only, freeze four timestamped landmarks
and candidate before its first output. At least3/4landmarks within2frames8fps,
plus all other frozen gates. Previous signer/synthetic/portrait are development
or regression clips. Never rename them held out. New-source failure stops
promotion with no tuning/reroll. One cycle; no model/dependency/feature expansion.

CPU verification: retain fine synthetic pixel signal versus the old false-highres
path; keep low-detail inputs/legacy helpers unchanged; test restoration of scoped
policies after exceptions. Confirm production object-swap source/graphs unchanged.
Public outputs use only cleared original art; human research media stays private.
