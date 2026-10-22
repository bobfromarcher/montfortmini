# Source geometry and prompt comparison — October19,2026

**The combination improves actual video color, scale and trajectory. Automated
gates pass; the full visual gate remains unmet because material/lighting is
excessively bright and saturated. Research-only; no production promotion.**

All four cells use the same known CC BY4.0 bee recording, original reference,
wide masks, seed42, VACE1.3B,20steps,CFG5,uni_pc/simple,shift8,strength1,
480×272,17frames,8fps. These are development comparisons, not held-out evidence.
The edited foreground ball mostly exhibits image-space drift; the bee pushes a different, beige ball. This does not test contact/occlusion involving the edited target. Only the control representation and positive prompt differ. One case/seed cannot
establish generalization or estimate stochastic uncertainty.

| Control / positive prompt | Green frames | Target/source area proxy | Result |
|---|---|---|---|
| Neutral fill / original instruction |17/17 |2.531 |Oversized baseline |
| Neutral fill / output description |17/17 |2.833 |Oversized, hole-like mark |
| Source luma / original instruction |0/17 |No green component |Smaller yellow target; reference fails |
| Source luma / output description |17/17 |1.106 |Color/scale improved; lighting/material fails |

The third cell changes graph node6 from OpenJutsuMediaInputs to
OpenJutsuLuminanceInputs. Source grayscale within the edit mask replaces flat0.5
fill; the outside RGB and all masks/reference/settings remain exact. The fourth
cell's complete input entries match the third; only4.inputs.text changes to the
previously tested output description. Against the original baseline, two graph
nodes differ. The fourth run was authorized as a separate final protocol after
the third exposed a smaller but wrong-color result; it was not preplanned before
the third output. No seed search or model switch occurred.

The executed custom node saves runtime-conditioning.npz. Its tensors match the
prepared archive exactly, including reference and masks. The retained control
also matches an offline calculation from the original PNGs; outside control RGB
is exact. Source revisions, graph, input/worker hashes and receipts pass the
offline checks. Comfy is5cc4b870094c89090db54bd8d12649dcaf89f2ba,SDK0.5.0,
proxy0.1.6; VACE files remain pinned to Comfy-Org/Wan_2.1_ComfyUI_repackaged@
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d. No claim about Genjutsu's server model.

Frozen gates were inherited unchanged: applicable visual dimensions>=3/4,
15/17 defining-attribute frames, no collapse/duplicate target, area proxy0.8–1.25,
centroid error<=0.1 diagonal, raw/encoded outside-region MAE<=3/255,p95<=10/255,
composite outside-mask max error0. Color-area segmentation is an imperfect size
proxy and cannot override visual failure.

The combination has17/17 green frames, mean centroid error0.004337 diagonal,
raw preservation MAE2.345/p957 and encoded1.770/p954. Composite preservation is
exact0. Raw and composite target-region PNG pixels match in all17 frames.
Provisional agent scores for each: coarse reference attributes3,motion3,
stability3,closed spherical shape3,scene lighting/material2. The green target
appears too bright/saturated with a soft edge/contact halo relative to the
supplied reference and scene. Thus overall gate_pass=false despite every
automated gate passing. Independent normal-speed professional scoring is pending.
The candidate is frozen for review, not approved for held-out quality testing.

Exploratory high-saturation foreground medians illustrate the mismatch:
reference RGB34/145/49 with encoded-RGB luma0.449; first source yellow221/146/30,
luma0.604; first generated green7/222/2,luma0.640. Different lighting and masks
confound these values. They are not calibrated reflectance, a new acceptance
threshold, or proof that source luma caused the remaining defect. A future
target-only luma normalization anchored to reference appearance could test that
hypothesis while retaining geometry and outside RGB. It has not been run. This
geometry-preserving method may also resist replacement with a different shape.

| New call | Worker / Comfy seconds | GPU samples / sampled peak |
|---|---|---|
| Luma only |52.481 /27.30 |51 /11,906MiB |
| Luma + description |36.898 /18.79 |36 /11,910MiB |

Call/SDK receipts: luma fc-01M5B5NZQ3VQK46SA32YWCPF03 /
86ae3a10-ece2-4a5d-8b95-20df90d672dd; combination
fc-01M5B5VKK51H49K4HFP79B3VY2 /fe960d09-be20-4f18-8c97-f4675deba20d.
Host peak RAM is unavailable: the cgroup file was missing; GPU samples remain
valid. Both protocols are closed, one call/660seconds/$0.75 included planning
ceiling each, combined$1.50. Live account usage8.41→8.44→8.47, remaining
credits21.59→21.53, cash charges/spend cap0. The$0.06 rounded account change
includes associated compute, not isolated invoices. No active containers remain.
No further inference, deployment or model change occurs in this continuation.

Offline commands from the repository root:

```powershell
python evaluation/audit_object_reference.py evaluation/object-luminance --luminance
python evaluation/audit_object_reference.py evaluation/object-luminance-prompt --luminance-prompt
python evaluation/render_object_comparison.py --factorial --output review/object-factorial
python -m unittest discover -s tests -p 'test_object_luminance*.py'
```

The first audit exits1 for the rejected yellow result; the second exits0 for
artifact/numerical gates only. Read review.json for the full visual rejection.
Fresh included-credit reproductions require a new directory and live observed
$LiveUsage/$LiveCredits with confirmed zero cash cap. The preparer dispatches
no inference; the controller rejects changed hashes or an existing ledger.

```powershell
python evaluation/prepare_object_luminance.py --output replay/luma --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_luminance_candidate.py --directory replay/luma --confirm-credits-only
python evaluation/prepare_object_luminance.py --output replay/combo --output-description --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_luminance_prompt_candidate.py --directory replay/combo --confirm-credits-only
```

Media/derivatives remain [CC BY4.0](SOURCE-LICENSE.md); original code is MIT.
The public108-second submission demo remains outdated. Independent review,
local native GPU reproduction, broader generalization and final cleared demo/
social/form materials are outstanding. Competition readiness is not established.

Verification:45 CPU tests pass in16.02seconds from a fresh Git source extraction; artifact audits and complete case inventories pass (25.20seconds including audits). Existing dependencies/same machine are not an independent clean installation or GPU reproduction. A [four-case label-blinded packet](blinded-review.zip) contains references, source/raw/finished videos and blank score sheets. No independent review has been received. A targeted scan of2026 files/ZIP entries found no known credentials or private human-media hashes; this is not a universal privacy/security audit.
