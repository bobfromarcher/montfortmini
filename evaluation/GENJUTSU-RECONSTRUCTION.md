# Genjutsu reconstruction: what is known and what is missing

Checked2026-10-18. This is a browser-client and public-interface investigation,
not recovery of Higgsfield's server source or model weights. No GPU job, paid
API call or generation submission was made for this investigation.

## The central correction

montfortmini is an independent open-model implementation, not a recovered
Genjutsu inference pipeline. Earlier reference-preparation experiments tested
our design hypotheses; their success or failure cannot identify Higgsfield's
implementation. Calling the current video generator a reverse-engineered clone
would overstate the evidence.

## Actual new evidence

The captured public editor HTML links125 JavaScript modulepreloads, totaling
6,642,481bytes. They were retained with URLs and SHA256 digests. One additional
2,031-byte request-builder module was followed from an explicit import. No
guessed internal endpoints, credentials or privileged server resources were used.
Initial requests using Python's default agent received403; ordinary requests
using the same Mozilla user-agent as the successful page fetch retrieved the
public assets. Both records remain. No authentication bypass was attempted.

The public client aliases`hf-mult-motion-control` to`genjutsu`. Its history/model
mapping handles distinct`HF_MULT_MOTION_CONTROL` and`HF_MULT_REPLACE_OBJECT`
job types. These are application routing labels; neither proves nor disproves
that Wan or another model powers the service.

The inspected motion request builder sends media references with image, optional
location, and source-video roles, plus prompt/resolution/scene settings. The object
builder sends source-video and image roles with prompt/resolution/size settings.
They construct asset references, not browser-side neural conditioning tensors.
There is no explicit mask field in the isolated object builder, but imported
helper spreads and server-internal segmentation are unresolved. This does not
prove that Genjutsu uses no masks or no image preparation internally. Array
ordering here must not be equated to image1/image2 conditioning in our Qwen node.

REA statically parsed three selected client modules,33,753bytes, without parse
failure. Retained parent Evidence:
ev_baa46c256ff4e22a0364a3e1c829b38410a9dd5955f3561649bffeafb08a513c.
Semantic coverage remains unknown with1,734unknowns; imported dependencies were
not all included in that focused analysis. Direct literal observations, source
digests and byte offsets are recorded separately in
[OBSERVED-CONTRACT.json](genjutsu-client/OBSERVED-CONTRACT.json).
This is not a claim that the whole application or any server path was traced.
Captured client code/REA bundle stay local and are not relicensed as our code.

The authenticated editor independently exposes two modes,4–30second input,
up to30reference images and720p default. Official API playgrounds expose separate
[motion-transfer](https://open.higgsfield.ai/models/higgsfield/genjutsu/motion-transfer/v1.0/playground)
and[object-swap](https://open.higgsfield.ai/models/higgsfield/genjutsu/object-swap/v1.0/playground)
models accepting video_url,image_urls,prompt and resolution. These docs expose
the service contract, not a downloadable model or inference graph. Their linked
full API reference redirects to API-account sign-in. No API account was created.
The[marketing page](https://higgsfield.ai/genjutsu) and older
[official guide](https://higgsfield.ai/blog/higgsfield-genjutsu) disagree on some
duration/reference limits; do not silently combine their numbers as one build.

The authenticated read-only draft tool corroborates the selected internal model
identifier. It also exposes an integration mismatch: it reports ready=true with
no blockers while the visible empty Genjutsu form has Generate disabled. Its
supported fields cover prompt/model/seed/enhance, not the visible Genjutsu video
and reference inputs. Its price mode is paid with no effective credit value.
Do not use that generic readiness result to assert a prepared/free Genjutsu run
or submit it. The tool response and simultaneous UI text are retained locally.
This observation does not establish the cause of earlier submission timeouts.

## Our actual missing capabilities

1. **Reliable scene/subject reconstruction.** Original-pixel registration keeps
   upper appearance but the missing lower body propagates into all33video frames.
   Free-form reference editors instead distort identity or clothes. Neither
   establishes a method that retains identity while adapting full-body framing.
2. **Reliable motion across reference poses.** Only2/4 frozen source events are
   provisionally matched on the latest development video. Prepared still quality
   cannot substitute for motion or unseen-recording evidence.
3. **Spatially correct local editing.** The current VACE1.3B/manual-rectangle path
   still fails realistic object scale/lighting. Exact outside-mask compositing
   repairs background pixels, but does not establish tracking, occlusion or
   object integration. Those behaviors need their own observed acceptance tests.
4. **A verified competitive target.** One retained private Genjutsu source,
   reference and output exists, but seed/backend/settings are unknown and our
   later crops/fps/durations differ. It is useful comparison evidence, not a
   matched superiority test or a reconstruction of its neural pipeline.

The motion-input audit rules out one tempting unsupported diagnosis: our current
WanAnimate2node is designed for raw driving video, not a required pose-skeleton
video. The pinned Comfy node schema/implementation accepts and encodes raw frames,
and the[official Wan-Animate-2 authors](https://github.com/Wan-Video/Wan-Animate-2/blob/main/README.md)
explicitly describe removing intermediate motion extractors. Do not transplant
Wan2.2-Animate pose/face preprocessing into Animate2 merely because both nodes
have an input named pose_video. This audit is not an endorsement of every
sampler, caption or framing choice in our pipeline.

## Consequence for the rebuild

The[Comfy competition](https://comfy.org/open-source-higgsfield) asks for working
open-source apps on the Developer Platform; it does not require extracting the
same hidden weights. Identifying those weights would help, but an observed
functional equivalent can use a different licensed open pipeline. Browser/API
inspection alone does not reconstruct undisclosed neural weights or training.

Keep the two-feature scope. The next motion implementation must produce a
complete, pose-compatible reference while protecting identity/wardrobe, then
pass the unchanged raw-video gates. A full-body reference or protected lower-body
outpainting is a specific unrun candidate, not an established Genjutsu stage or
proven fix. Retain the source-first-frame oracle as a diagnostic control; its
success does not prove identity replacement. Object work needs target scale,
lighting and occlusion integration, not a broader UI.

No model replacement, dependency installation, default change or new GPU
experiment follows from a branded client routing string. The previous phase
remains stopped. A new inference cycle needs an explicit bounded included-credit
budget and a frozen comparison capable of changing the quality decision.
Current result: useful client-contract reverse engineering, server/model identity
unresolved, convincing open replacement still unachieved.
