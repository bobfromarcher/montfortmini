# Reference-branch sensitivity — October 21, 2026

**The reference branch measurably affects output, but the effect is too small
for convincing reference transfer in this case. Both outputs remain beige.**
This is a completed diagnostic pair, not a passing video-quality candidate.

The previous loader recomputed control brightness/chroma from the reference.
Simply replacing reference.png would therefore have changed two inputs. The
new research-only loader reads frozen control/mask/reference arrays, decoupling
the reference branch. A transparent receipt node records the conditioning
entering the sampler and returns the original objects unchanged.

Both new arms share the same graph, text, source-derived green control, masks,
VACE1.3B, seed42,20steps,CFG5,uni_pc/simple,shift8,strength1,480x272/17f/8fps.
The first repeats the original green reference; the second changes only its
foreground chromaticity to magenta. Reference encoded luma/shading is preserved
within5.96e-8, with zero clipping or outside-reference changes. The reference
tensor remains float32; branch-reference.png is a quantized preview. Original
reference.png remains unchanged as control-preparation provenance. Actual NPZ
tensors, not previews, are authoritative.

The [protocol](PROTOCOL.json) was frozen before either new output. A repeat
failure or invariant/technical failure would block the second call. The known
beige quality failure was expected in this diagnostic control. The fresh repeat
matches the prior raw video **pixel for pixel across all17 frames**, establishing
that the frozen loader/receipt preserve this observed result.

At the actual sampler boundary, native receipt tensors are float32. Positive
text, negative text, encoded control tail, VACE mask and initial latent are
bit-identical between arms. Only the encoded reference prefix changes (maximum
absolute element delta8.390625). Both use the same one-reference/five-control
packing, initial latent shape1x16x6x34x60, seed and graph. Actual generated noise
values are not independently captured; same seed/latent setup is verified.

| Measurement | Result |
|---|---:|
| Repeat versus prior raw maximum pixel error |0/255 |
| Reference-only foreground mean RGB change |1.912/255 |
| Reference-only whole-frame raw mean change |0.508/255 |
| Raw outside-edit mean change between arms |0.404/255 |
| Composite outside-edit change between arms |0 |
| Frames with positive reference-direction chromaticity shift |15/17 |
| Median signed output chromaticity projection |0.001270 |
| Reference chromaticity displacement |0.52996 |

The response meets the preregistered diagnostic rule: foreground change>1/255
(repeat error is0), with positive reference-direction projection in>=15/17
frames. The effect is small: the descriptive median projection/input-displacement
ratio is about0.0024. That is not an attention weight, physical transfer gain,
identity percentage or population estimate. Correlated frames provide no
independent sample of17 videos. A threshold pass here cannot pass visual quality.

All17 counterfactual raw frames were inspected, alongside the pixel-identical
repeat/baseline. Both targets remain beige/brown, with clear reference color and
material mismatch. Conservative raw/composite scores for both: reference1,
motion3,stability3,shape3,material/lighting2. Raw/composite target PNG pixels match
exactly. Raw background preservation MAE/p95 is2.374/7 for repeat and2.249/7 for
counterfactual; composite outside-mask PNG error is0. Independent normal-speed
professional review remains outstanding. No quality winner, held-out generation,
production visual promotion or deployment follows.

These observations establish an active but weak reference response for this
setup. They do not identify the cause of that weakness. Text binding, competition
from fixed green reactive control, reference encoding/attention and model capacity
remain competing explanations. The magenta reference deliberately conflicts with
green control to isolate the reference branch; the original aligned green arm
also fails appearance. No conclusion about Higgsfield's backend follows.

The next correction should target effective reference conditioning. A controlled
capacity comparison or a targeted text/control-competition test would test
different hypotheses; neither is justified as a guaranteed remedy or run here.
Repeated brightness/chroma preparation has no demonstrated route to full fidelity
in the retained studies. Scope stays object replacement and character motion;
this diagnostic does not change the deployed character-motion path.

| Resource | Repeat | Counterfactual |
|---|---:|---:|
| Worker seconds |46.292 |45.346 |
| Comfy graph seconds, including loading |23.67 |21.68 |
| CPU-preflight client interval, including startup/transfer |13.164 |10.596 |
| GPU samples |45 |44 |
| Sampled peak VRAM, L40S |11,905MiB |11,905MiB |

Host peak RAM is unavailable (missing cgroup path); sampled VRAM is not a
continuous allocator peak. Modal calls fc-01M5FGS5AADZ7QZR89MP4JPFXA and
fc-01M5FGYHC70RXPKH3TE004MJ9G; SDK jobs9daf0b72-33f4-464e-8f6f-b8bf492a48b8
and15617417-fbb0-41c3-b59a-656fb5b7669a. Model revision
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d, Comfy
5cc4b870094c89090db54bd8d12649dcaf89f2ba,SDK0.5.0/proxy0.1.6 unchanged.
Exact original inputs, actual tensors, workflows, model/source provenance,
freezes, receipts, failure decisions, logs and resource samples are retained.
The inherited runtime target-erased flag is inaccurate for this frozen control;
original manifests are preserved and actual NPZ/control graph are authoritative.

Two planned calls cap660seconds/$0.75 included each, diagnostic maximum$1.50,
plus$0.75 verification reserve, total$2.25/cash0 and at least$2 remaining. Both
calls complete; the protocol is closed with no retry. Rounded account usage
8.59->8.65, included credits21.41->21.35, cash charges/spend cap0: approximately
$0.06 account delta including CPU/builds/rounding, not isolated invoice cost.
Final container list is empty. No new dependencies, models or infrastructure.

```powershell
python evaluation/audit_reference_branch.py evaluation/reference-branch --parent evaluation/object-color-prompt
python evaluation/render_reference_branch.py --output review/reference-branch
python -m unittest discover -s tests
```

Audit exit0 means diagnostic isolation/repeatability, not quality. Fresh inference
requires live billing, zero cash cap and a new directory. Preparation dispatches
nothing. The second arm is blocked until repeatability.json passes:

```powershell
python evaluation/prepare_reference_branch.py --output replay/reference-branch --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run reference_branch_candidate.py --directory replay/reference-branch/repeat --confirm-credits-only
python evaluation/audit_reference_branch.py replay/reference-branch --parent evaluation/object-color-prompt --repeat-only
python -m modal run reference_branch_candidate.py --directory replay/reference-branch/counterfactual --confirm-credits-only
```

One development recording/seed, fixture-specific foreground oracle, mostly
image-space target drift; the bee pushes a different ball. No contact/occlusion,
arbitrary-shape, independent generalization or character-motion claim. Code MIT;
bee source/derivatives CC BY4.0 with [attribution](SOURCE-LICENSE.md). Independent
review and GPU reproduction remain pending; overall submission readiness unmet.

Verification:61 CPU tests pass in19.568seconds from a fresh Git extraction; complete source/artifact audit51.524seconds. Pair isolation passes and repeat is pixel-exact. Existing dependencies/same machine, not independent GPU reproduction or clean installation. Only report/status metadata changed afterward. Targeted known-secret/private-media scan3267 files/ZIP entries,0 issues; not universal audit. Label-blinded packet preserves both conditions with separate appropriate reference previews and blank review forms; no external scores received.
