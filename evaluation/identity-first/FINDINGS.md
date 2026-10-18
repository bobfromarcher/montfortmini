# Identity-first and original-pixel preparation — 2026-10-18

**Rejected for production and submission.** One new development video retains
the defining reference attributes much better, but the character floats as a
thigh-truncated cutout throughout. Recognizable motion timing is not established.
This is a partial appearance improvement in actual model output, not a passing video.

## What ran and what the evidence supports

| Candidate | Controlled comparison | Observed result | Decision |
| --- | --- | --- | --- |
| Identity-first Qwen | Same two prepared images, latent canvas, generator, seed and sampler as prior pose-first control; swap image roles and relabel prompt image numbers | Rear-facing subject; face and front shirt unassessable, blazer-like rear hem/cuffs visible | Fail; no inference that the hidden shirt was deleted |
| Identity-first + depth | Same first two image arrays; add estimated inverse-depth as image3 and a textual orientation role | Frontal orientation improves, but face distorts, headwear appears and T-shirt replaces required blazer/light shirt | Fail; depth plus text is a bundled ablation, not a depth-only causal estimate |
| Registered original pixels → Animate2 | Same executed video graph, source/mask arrays, seed, sampler and model as historical cascade control; prepared reference changes | Glasses/curls/beard/face recognizable in conservatively 31/33 frames; blazer/light shirt in 33/33; missing lower body in 33/33 | Fail; no production promotion or unseen-source inference |

The final preparation segments the original fictional subject with MediaPipe,
registers its torso by a uniform 2D similarity transform to the source torso,
and uses a neutral backdrop. It does not redraw the face/clothes, mirror the
subject or squeeze facial geometry. Interpolation and alpha-edge blending are
explicit preprocessing, so “original pixels” does not mean byte-identical output.
It retains the original neutral pose and upper-thigh crop. No missing body
regions are synthesized. No generated video pixels are pasted over afterwards.

The selected video branch reuses that CPU reference archive and executes only
Wan Animate2 through the existing official Comfy SDK 0.5.0/proxy 0.1.6 path.
Qwen and Klein are not executed for that video, even though their helper files
appear in imported module/source inventories. The executed graph and conditioning
arrays, not import names, establish this inference path. The video is 480×560,
33 frames, 8fps, seed42, 10 steps, CFG1, LCM/simple, shift5. Exact workflow,
environment, model revisions/hashes, SDK receipts and generated frames are retained.
No Genjutsu internals are observed or inferred from these experiments.

## Frozen gates and review limits

The inherited rubric requires every applicable visual dimension >=3/4, >=28/33
frames retaining defining attributes, plausible anatomy throughout, and >=3/4
source motion events within ±2 frames at8fps. Criteria were not relaxed after
viewing output. All33 source/raw pairs and face crops were reviewed. Provisional
agent scores: reference3, motion2, temporal3, anatomy1, photorealism/scene2.
Frames1–2 have uncertain glasses/face detail from blur;31/33 is an attribute
retention count, not a face-verification score or proof of exact identity.
Only2/4 timing events are clearly recognizable in manual frame comparison;
the cross-torso and hand-to-mouth events are not established. Head motion is weak.
There is no independent professional score or normal-speed professional playback
review. These limits cannot turn the unequivocal missing-body failure into a pass.

Raw and composite decisions are both FAIL. All33 corresponding PNG arrays and
the encoded MP4s are identical because the mask covers the full frame. The gray
scene and missing lower body are raw model behavior, not compositing repairs.
No outside-region/background preservation is demonstrated. Object replacement
was not changed or rerun; its prior realistic scale/lighting failures remain.

## Protocol deviations — retain the original rules

1. Original branching required an identity/clothing pass before adding depth.
   The rear view made them unassessable. An explicit pre-output exploratory
   amendment allowed depth anyway. This did not satisfy the original branch.
2. Depth then failed. A second pre-output amendment allowed a different CPU
   preparation candidate to bypass the generative-still pose gate and run one
   development video. Its neutral pose/cropped-body limitation was recorded.
   The amendment required stopping on any video failure. That stop is now enforced.

Both amendments and original freezes are included verbatim. These are exploratory
development results, not a preregistered confirmatory success. No fourth GPU call,
reroll or unseen test was run. Former signer/portrait/synthetic cases remain
development; temporal crops or mirrors would not count as independent recordings.

## Resources and verification

Declared hard cap: $3 additional included credits,4 GPU calls,3000 worker seconds,
with verification reserved before dispatch. Actual:3 GPU calls,1053.314 measured
wrapper seconds;1980 seconds reserved at full ceilings. Video worker136.047s
excludes cached reference preparation. Sampled video peak VRAM28,604MiB;64GiB
RAM is allocation, not measured physical peak. See resource-summary.json for
per-run times/VRAM. Cost summary changed $6.45→$7.21; remaining $23.55→$22.79,
displayed $0.76 included-credit delta; cash$0, spend cap$0. These asynchronous
account readings are not exact per-job invoices; disagreeing animated breakdown
and CPU/build overhead are explicitly retained. Final active container list is empty.

The19-test suite passed, plus the new registration geometry test passed separately.
All frozen inference source hashes match. Both paired reference graph audits
passed. The video audit passed decoding, dimensions, frame counts and raw/composite
equality, while assigning no perceptual pass. Initial local image-composition and
CPU mask-shape failures were fixed before their GPU dispatch, and retained.
No generation retry occurred. The depth CLI timed out collecting final app logs
after its complete successful output was already saved; this was not a generation
failure or resubmission. Independent clean-machine GPU reproduction remains pending.

MediaPipe task model is Apache2.0; its recorded card/SHA are in the previous pose
study. Depth Anything V2 Small HF is Apache2.0, revision
5426e4f0f36572d16453bbda7a8389317b1bef99; its99,173,660-byte weight SHA is
3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70.
Relative inverse depth is percentile-normalized, not metric depth or normals.
Video/generator weight revisions and licenses remain the recorded open assets.
Source licensing/provenance and original inputs remain in the private evidence.
Human-source derivatives remain private: promotional likeness permission is not
established. Public metadata excludes derived human media and landmark arrays.

## Release decision and the specific next change

No convincing full-frame video, independent-held-out pass, independent reproduction
or professional approval is established. Existing cleared108-second demonstration
and production path remain unchanged. Official competition readiness is blocked by
quality and independent verification, plus unverified formal registration/social
and submission steps. No new social post, submission or merge is performed.
The official rules checklist and cleared demonstration remain in submission/.
Eligibility and any prize remain the organizer's decision.

The demonstrated limitation is that this prepared reference lacks the lower body
and the animation does not reconstruct it. The next justified technical candidate
would require a compatible full-body reference or masked lower-body outpainting
that protects the original face and upper clothing. That is an untested hypothesis,
not a proven fix; further motion timing validation would still be required. The
evidence does not demonstrate a need for a larger GPU. Do not hide the defect by
cropping the result or substituting source legs after generation.

## Reproduction commands

From the repository root, install requirements.txt and evaluation/requirements.txt.
Optional CPU registration uses a separate Python3.11 environment with
evaluation/requirements-pose.txt and the exact verified MediaPipe task file.
Inputs and outputs below refer to the private evidence archive; intentionally no
performer-derived media is published as a competition demo.

```sh
python -m unittest discover -s tests -v
python registered_reference.py --source SOURCE_FRAME.png --identity ORIGINAL_REFERENCE.png --source-landmarks SOURCE_LANDMARKS.json --model pose_landmarker_full.task --output NEW_REFERENCE_DIRECTORY
python evaluation/audit_identity_first.py --control EVIDENCE/pose-control --candidate EVIDENCE/study/anchor --output order-audit.json
python evaluation/audit_depth_reference.py --control EVIDENCE/study/anchor --candidate EVIDENCE/study/depth-anchor --output depth-audit.json
python evaluation/audit_cascade.py --run EVIDENCE/study/registered-motion --compare EVIDENCE/video-control --output video-audit.json
python -m modal run identity_first_candidate.py --help
```

Offline commands do not launch inference. Remote replay needs fresh authorized
included-credit observations, original private inputs/case paths, matching
code/model hashes and a new explicit experiment protocol; the saved stopped
ledger must not be deleted to obtain retries. The exact executed graph is retained
in the private packet for independent inspection without rerunning inference.
