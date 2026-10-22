# Guidance contrast — October 21, 2026

**Lowering CFG from5 to1 did not restore reference fidelity. The target is red
in all17 frames, versus beige in the matched CFG5 baseline. Both fail.**
The original reference and source-derived control remain green. No production
defaults or character-motion settings change, and no verification generation
follows this failed development candidate.

Only `9.inputs.cfg` changes. The complete input ZIP is byte-identical to
`../reference-branch/repeat/inputs.zip`. Actual source, masks, reference,
positive/negative text, encoded VACE reference prefix, control tail, mask and
initial latent tensors are bit-identical at the measured sampler boundary.
Seed42,20steps,uni_pc/simple,shift8,strength1,480x272/17frames/8fps, model
revision123acf1cc74bccbb9bfff8ac1ee72edc08c2341d and Comfy
5cc4b870094c89090db54bd8d12649dcaf89f2ba are unchanged. The graph, source
snapshots, tensor receipts and original logs are retained. Actual sampler noise
values are not independently recorded.

The [protocol](PROTOCOL.json) and [acceptance criteria](freeze.json) were frozen
before inference: every visual dimension>=3/4, defining reference attributes in
>=15/17 frames, no collapse or duplication, area proxy0.8–1.25, centroid mean
error<=0.1 diagonal, raw/encoded outside-region MAE<=3 and p95<=10/255,
composite outside-mask PNG error0. Color statistics cannot override visual failure.

The pinned [default sampler](https://github.com/Comfy-Org/ComfyUI/blob/5cc4b870094c89090db54bd8d12649dcaf89f2ba/comfy/samplers.py#L592)
uses conditional-minus-unconditional extrapolation. At CFG1 its default
optimization skips unconditional prediction; positive text remains active.
This is not image-only generation or a direct reference-strength adjustment.
Negative conditioning was provided and captured; actual prediction count was
not independently instrumented. No custom CFG hook is present in this graph.

| Measurement across the same17 development frames | CFG5 baseline | CFG1 |
|---|---:|---:|
| Frames with green generated target |0 |0 |
| Observed target color |Beige/brown |Red/orange |
| Median fixed-ROI reference chromaticity distance |0.40831 |0.54969 |
| Median encoded luma |0.51660 |0.43424 |
| Median HSV saturation |115 |171 |
| Median adjacent-frame RGB-median step |1.732 |2.571 |
| Maximum adjacent-frame RGB-median step |5.385 |7.071 |
| Raw outside-region MAE/p95, /255 |2.374/7 |2.094/6 |
| Composite outside-mask PNG maximum error |0 |0 |

The fixed-source eroded ROI counts wrong-color pixels rather than selecting
only green generated pixels. CFG1 is closer to reference brightness while
farther in chromaticity. Brightness alone therefore remains an inadequate
success metric. Adjacent median-color steps are descriptive, not
motion-compensated flicker or independent-video statistics. The green-based
area/centroid proxies are null when green is absent; that does not demonstrate
geometric collapse.

All17 raw frames and the selected paired frames were inspected. Conservative
provisional raw and composite scores are reference1, motion3, stability3,
shape3, material/lighting2. The wrong reference color is decisive regardless
of the provisional passing dimensions. Raw and composite target PNG pixels
are identical; the compositor has not corrected the target. The edited ball
mostly drifts, while the bee pushes another ball. This is not contact/occlusion
evidence or a character-motion/generalization test. Independent normal-speed
professional review remains outstanding; a blinded packet is provided.

**Decision: reject CFG1 and close this protocol.** The measured reference path
was already active but weak. This result rejects this specific guidance
remedy. It does not prove that every guidance setting fails, that VACE1.3B is
incapable, or that a larger checkpoint will solve the problem. Reference
encoding/attention, control competition and learned model behavior remain
possible causes. No claim about Higgsfield's backend follows.

Repeated control brightness/chroma preparation, prompt-only tuning and this
guidance intervention have not produced a full pass. A controlled checkpoint
capacity comparison is now a credible next test, subject to a separate frozen
budget and feasibility gate; see [candidate feasibility](CAPACITY-CANDIDATE.md).
No further inference, model download or new infrastructure occurs here.

Worker39.479seconds; Comfy graph19.98seconds including loading; CPU-preflight
client interval8.904seconds including startup/transfer. L40S39 GPU samples,
sampled peak11,653MiB. Host peak RAM unavailable because the cgroup path was
absent. Call `fc-01M5GTFP7ZBVDB63KJ791R37RV`, SDK job
`e1058dcc-bb51-4f2a-a244-26b72308280e`, SDK0.5.0/proxy0.1.6. Receipt float32
arrays do not imply every model operation used float32.

One attempt was permitted, <=660seconds/$0.75 included; $1.50 verification
reserve was conditional on a full pass and remains unused. Initial expired
authentication failed before GPU reservation; same-scope12h refresh preceded
the single actual GPU call. Rounded account usage8.65→8.69, credits21.35→21.31,
cash charges/spend cap0. The approximately$0.04 account delta includes CPU,
builds and rounding; it is not an isolated invoice attribution. Final container
list empty. Exact originals remain in the private evidence archive as well
as this public case.

The original generic `target_erased_in_control=true` metadata flag is inaccurate
for the frozen research control. Original manifests are preserved; actual NPZ
and graph are authoritative. This known development recording is not unseen.
Competition submission readiness remains unmet: convincing visual quality,
independent footage, independent review/reproduction and an updated cleared
two-minute demonstration remain outstanding. This failure package is evidence,
not a competition success claim.

Recompute locally without inference, from the repository root:

```powershell
python evaluation/audit_guidance.py evaluation/guidance-balance
python evaluation/object_color_diagnostics.py --inputs evaluation/guidance-balance/inputs.zip --baseline evaluation/reference-branch/repeat --candidate evaluation/guidance-balance --output guidance-diagnostics.json
python evaluation/render_object_comparison.py --guidance --output guidance-comparison
python -m unittest discover -s tests
```

The audit deliberately exits1 for this quality failure. Its `isolation_pass`
must still be true. FFmpeg is required for comparison rendering. The GPU
controller refuses an existing ledger; do not remove the ledger to retry.

Fresh Git extraction verification:61 CPU tests pass in16.801seconds. The
conditioning isolation audit reproduces its pass; quality rejection/exit1 is
expected. All-frame color diagnostics recompute exactly. An initially incorrect
documented --inputs directory was corrected to inputs.zip and then verified.
Same machine/existing dependencies; no clean install, independent GPU replay
or professional review. The source-tree identity is in clean-verification.json.
