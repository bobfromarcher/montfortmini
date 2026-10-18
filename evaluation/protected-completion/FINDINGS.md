# Protected reference completion — 2026-10-18

**Actual raw-video body truncation fixed; overall quality gate still FAIL.**
Motion remains2/4 clear frozen events, below the required3/4. No independent
recording was generated, no production promotion occurred, and this is not a
finished Genjutsu replacement or submission-ready result.

| Development evidence | Previous registered reference | Protected completed reference |
| --- | --- | --- |
| Continuous body through lower frame edge | 0/33 frames | 33/33 frames |
| Defining attributes, conservative manual assessment | 31/33 clear | 31/33 clear |
| Blazer/light shirt | 33/33 | 33/33 |
| Clear source timing events, ±2frames | 2/4 | 2/4 — FAIL |

All33 source/control/new-raw frame triplets were reviewed at native size.
Attribute counts and ordinal scores are provisional coding-agent assessments,
not independent professional or biometric verification. Frames1–2 are counted
uncertain because of blur. Hands have visible motion blur; head orientation
is weak. Normal-speed independent professional playback review is outstanding.

## Implemented correction and exact comparison

The existing registered original-pixel reference supplies the face, glasses,
curls, beard, cobalt blazer and ivory shirt. A binary mask edits only its lower
24%, beginning at row570/750. The existing pinned Qwen2511 graph adds
LoadImageMask→SetLatentNoiseMask, retaining40Euler/simple steps, CFG4, seed42.
Its generated missing-body region is combined with exact original reference
pixels outside the mask. No output-video pixel is pasted over or repaired.

The first Qwen output completes the trousers but introduces an unrelated enlarged
body/image fragment in the lower-right edit region. It fails the original
reference gate and is retained. One existing-model CPU person segmentation pass
removes that fragment from the prepared reference. Outside-mask reference error
is exactly0 after both protection and isolation. The unchanged video graph then
generates the entire clip from that reference and the original driving footage.

The video audit confirms identical source/mask arrays, model/seed/sampler and
executed graph versus the truncated control. Prepared reference rows0–423/560
are identical; only rows424–559 change. The corrected raw clip has continuous
legs in every frame. This matched development experiment supports the reference
crop as the cause of the truncation in this case. Body completion alone does
not solve the gesture failure. No universal model limitation or Genjutsu-internals
claim follows. Both raw and composite PNGs/MP4 are identical under a full-frame
mask, so they receive the same motion FAIL. Source background preservation is
not established.

The four source-only events remain frozen. At source8 the two-arm cross-torso
configuration is not clearly reproduced in candidate6–10. Source16 has a
provisionally recognizable match at14; source24 has lowered hands at23.
The mouth event at28 is not established in26–30: the generated hand remains
nearer the throat/chest. No event definitions, tolerances or passing threshold
were changed. All other visual dimensions score provisionally3/4; motion2/4
prevents an overall pass. The prior real-object scale/lighting failure remains
unaddressed by this motion-only correction.

## Protocol deviation and setup defects

The declared rule would stop after the first reference failure and allow no
amendments. We explicitly deviated once, before CPU isolation and video output,
to address the newly observed unrelated panel using an existing CPU model.
This is exploratory development, not preregistered reference success. The GPU
budget and video acceptance criteria stayed fixed. After the video motion
failure, work stops without another amendment, reroll, model switch or third call.

CPU preflight first caught a missing module mount before any GPU reservation.
It was repaired and refrozen before generation. CPU segmentation then aborted
natively on650×750, both before/after moving mask copying into detector lifetime.
Using640×736 for CPU inference, then resampling its mask back, succeeded; these
failures are retained. That observation supports the dimension-aligned workaround,
not a complete diagnosis of MediaPipe's native implementation. The regression
test checks alignment, fragment isolation and exact protected pixels.22tests
passed together, plus the new isolation test passed separately. All10 frozen
inference/preparation source hashes still match.

## Resources, reproduction and release

Hard cap:$2 additional included credits,3GPUcalls,2220reserved worker seconds.
Actual:2calls,526.477wrapper seconds;1320seconds reserved at full ceilings.
Qwen388.824s; video137.516s excluding reference/local CPU preparation. Sampled
video peak28,444MiB VRAM; see resource-summary.json for both peaks.64GiB RAM is
allocation, not measured physical peak. Modal cost summary7.21→7.59, remaining
22.79→22.41: displayed$0.38included-credit delta, cash$0 and cash cap$0.
Account readings may lag and are not per-job invoices; the disagreeing animated
breakdown and CPU overhead are disclosed. Final container inventory is empty.

No new generator, adapter or model weights were introduced. Existing Qwen/Wan
weight revisions/licenses remain recorded; the CPU MediaPipe model is the
previously verified Apache2task bundle, SHA256
4eaa5eb7a98365221087693fcc286334cf0858e2eb6e15b506aa4a7ecdcec4ad.
Optional CPU environment uses Python3.11, MediaPipe0.10.35, NumPy2.4.6 and
Pillow13.0.0. Production/default inference and cleared108-second demo remain
unchanged. Human-source derivatives stay private; only code and evidence metadata
are public. Independent professional review and clean-machine GPU reproduction,
realistic object quality and formal competition submission remain outstanding.

```sh
python -m unittest discover -s tests -v
python evaluation/audit_protected_reference.py --run EVIDENCE/reference --output reference-audit.json
python isolate_reference_subject.py --reference EVIDENCE/reference/anchor.png --base EVIDENCE/reference/base.png --edit-mask EVIDENCE/reference/edit-mask.png --model pose_landmarker_full.task --output NEW_ISOLATED_REFERENCE
python evaluation/audit_cascade.py --run EVIDENCE/motion --compare CONTROL/registered-motion --output video-audit.json
python -m modal run protected_candidate.py --help
```

The private packet includes original input bytes, frozen preparation bundle,
raw Qwen failure, CPU masks and successful reference, every source/raw/composite
frame, executed graphs/SDK receipts/environments, controls, hashes and logs.
Remote replay requires a new authorized budget, original inputs and explicit
review gates; do not delete the stopped ledger to obtain retries. The unused
complete branch predates CPU isolation and is not a validated fresh execution
of the amended candidate. Its quality gate is blocked; do not claim it provides
unseen-source reproduction of this study.

The next change must address motion transfer itself while keeping this completed
reference fixed. A concrete candidate is an explicit per-frame body/hand/face
control path in an appropriately licensed animation/replacement model, compared
against these same frozen events. Its identity fidelity and timing would need
demonstration; it is not a proven fix or an inference about Higgsfield. More
reference completion variants are not supported by the current failure.
