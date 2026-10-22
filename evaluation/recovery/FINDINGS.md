# Recovery findings — October18,2026

**Decision: realistic quality target remains unmet. Do not promote the cascade.**
The deployed app remains on its documented VACE/Animate2 path. Object replacement
was not changed; the real-object scale/lighting failure remains disclosed.

A source-pose-matched reference recovered seated framing and hand performance on
one difficult private development clip. Paired controls kept source pixels,
masks and the video graph identical. That supports reference composition as a
material cause on this clip. The final experimental recipe was Klein4B → Qwen
Edit2511 → existing Wan Animate2, using pinned open weights and official SDK.
Qwen refinement gave a closer development face than Klein alone. Stronger pose,
a base-model recipe, higher reference strength and original-portrait CLIP
conditioning offered no persuasive solution or further gain.

The candidate was frozen before its first new CC0 recording. That test failed:
0/33 frames retained the defining glasses, versus the required28. The source
headwrap remained; Qwen stylized the face before animation. Blue clothing alone
does not establish identity. The known synthetic regression transferred broad
arm raising but invented a bedroom, changed illustration style and incompletely
matched lowering. It was not an independent holdout. No tuning followed either
test and no successful-generalization claim is made.

| Final-phase experiment | Worker seconds | Result |
|---|---:|---|
| Qwen generic reference edit |396.29|Closer face; wrong shirt, invented phone|
| Qwen with target caption |389.06|Outfit recovered; composition changed|
| Qwen refining Klein output |387.01|Best development reference; pattern drift|
| Cascade development motion, cached reference |261.14|Better face/framing/hands; video-only latency|
| Original-portrait CLIP input |260.64|No persuasive improvement|
| Reference strength1.3 |206.48|No persuasive improvement|
| New-recording full cascade |579.95|Identity/realism fail|
| Known synthetic full cascade |506.22|Style/background/timing regression|

Eight GPU attempts totaled **2986.80 measured worker seconds**, below3600.
Both final tests used fresh3-stage inference; the development motion timing
excludes cached reference preparation. L40S sampled peak VRAM was30,654MiB
(new recording) and30,910MiB(synthetic). Worker RAM allocation was64GiB;
physical peak RAM was not measured. All final raw/composite PNG arrays matched
exactly because the motion mask is full-frame. All MP4s decoded at the declared
8fps, size and17/33frames. This does not establish source-background preservation.

The billing snapshot displayed5.62 total credit use and6.1996 in its breakdown;
provider totals lag/disagree. Against the3.38 phase baseline this is2.24 displayed,
or up to2.8196 conservatively. **Cash spend and cash cap are both$0.** The higher
total is below the original6.23 overall stop. All experimental apps are stopped;
container inventory is empty. No further GPU calls are permitted in this study.

The historical new input was reconstructed byte-for-byte from its verified
public original and recorded FFmpeg command. Runtime source hashes remained
unchanged. The final report retains pre-call budget revisions rather than
rewriting their history. Technical checks and agent ratings are not independent
professional review. Four fully timestamped motion landmarks were not frozen,
so a formal3/4 timing pass cannot be claimed. Independent blinded scoring,
full GPU reproduction and real-quality success remain outstanding.

See [reproduction guide](../RECOVERY.md), frozen protocols, technical audits,
resource-summary.json and the public synthetic review packet. Human research
media and private development portraits are excluded from public submission
media. The updated108-second demo and social/form drafts represent the failure
honestly. Registration, social publication and formal submission remain pending;
no guaranteed eligibility or prize is claimed.

Fresh checkout verification:10 production tests+2 geometry tests passed; all11 frozen runtime-source hashes matched. Offline audit passed and input reconstruction matched byte for byte. See SETUP-CHECK.md for the tested commit and practical limits.
