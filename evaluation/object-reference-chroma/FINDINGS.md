# Reference-chromaticity contrast — October 21, 2026

**Rejected: adding reference chromaticity did not resolve the raw video's
material mismatch. No production visual change or unseen generation follows.**

The previous reference-luma candidate preserved scale and trajectory but rendered
a neon green object. This single-factor test adds the original reference's
foreground median RGB/luma ratio to the reactive control, using the existing
5x5 sigma1 foreground feather. One fixed ratio applies to all17 frames; no
generated pixels influence preparation. The original source/reference/edit and
foreground PNGs, gain0.741566, prompt, VACE1.3B, seed42,20steps, CFG5,
uni_pc/simple, shift8, strength1 and480x272/17frames/8fps remain fixed.
Only graph node6's loader and the derived source-control tensor differ.

The actual-image CPU preflight reproduced the prepared control exactly and
checked the installed custom-node bytes. During inference the executed node
saved its returned tensors; these also match preparation exactly. Encoded RGB
luma changes at most1.788e-7 versus the previous control, below the frozen2e-7
instrumentation tolerance; zero values clip. Outside-control pixels are exact.
The pinned Comfy WanVaceToVideo node encodes the supplied masked RGB in its
reactive branch; this input is not simply erased before conditioning. Its
influence after VAE/denoising is not separately measured here.

| Measurement | Prior reference-luma | Reference chromaticity |
|---|---:|---:|
| Green raw/composite frames |17/17 |17/17 |
| Target/source area proxy |0.9553 |0.9219 |
| Mean centroid error/image diagonal |0.003609 |0.003692 |
| Raw outside-region MAE/p95, /255 |2.368/7 |2.312/7 |
| Encoded outside-region MAE/p95, /255 |1.771/4 |1.770/4 |
| Composite PNG outside-mask maximum error |0 |0 |
| First-frame foreground median RGB |5/187/6 |11/203/5 |
| First-frame median encoded luma |0.536 |0.589 |
| Provisional scene material/lighting score |2/4 |2/4 |

Reference median RGB is34/145/49 and encoded luma0.449. The new output is
brighter than the prior candidate and remains strongly saturated, despite
unchanged control luma. These first-frame, segmentation-dependent summaries
are exploratory, not calibrated reflectance, additional acceptance thresholds
or estimates of a population effect. No statistical significance is claimed
from one recording and seed. All17 raw frames were inspected. Raw/composite
target PNG pixels are identical: compositing does not repair the material.
Other provisional visual dimensions score3/4; material/lighting remains2/4.
All numerical gates pass, but the frozen full visual gate fails. Independent
normal-speed professional review remains outstanding.

This rejects the practical hypothesis that this chromaticity intervention
alone remedies the known failure at these settings. It does not identify the
remaining cause. Repeated color words in the positive prompt, insufficient
reference influence and model capacity remain competing hypotheses. A
color-word-only prompt ablation would discriminate prompt pressure before
another model change; it has not been run under this closed protocol.

Limitations: inherited fixture-specific HSV foreground oracle, same development
recording and seed, synthetic shaded sphere reference, no arbitrary shape
replacement, contact or occlusion evidence. The bee pushes another ball; edited
target motion is mostly image-space drift. No new held-out evidence, generic
segmentation result, Genjutsu architecture discovery or overall readiness claim.
The retained runtime manifest's generic `target_erased_in_control=true` field
is inaccurate for this research loader: source geometry/luma and reference
chroma are explicitly retained. Exact runtime tensors and graph are authoritative.
The original runtime manifest is preserved without rewriting its observations.

Worker47.635seconds; Comfy graph23.88seconds including loading;47 GPU samples,
sampled peak12,929MiB on L40S. Host peak RAM unavailable (missing cgroup path);
CPU-preflight duration not separately measured. Modal call
fc-01M5FC4PW05KY5GYXTRK6RS7GD; SDK job
0e0ada8f-e14f-46c4-ad7b-c67e941d10a0. Models remain pinned to
Comfy-Org/Wan_2.1_ComfyUI_repackaged@123acf1cc74bccbb9bfff8ac1ee72edc08c2341d;
Comfy5cc4b870094c89090db54bd8d12649dcaf89f2ba; SDK0.5.0/proxy0.1.6.
Exact workflows, snapshots, original inputs, runtime tensors, logs, resources
and receipts accompany this report. Code MIT; media attribution and CC BY4.0
terms are in [SOURCE-LICENSE.md](SOURCE-LICENSE.md).

Budget declared before dispatch: one development call <=660seconds/$0.75
included; total cycle ceiling$2.25, reserving$1.50 for verification only after
full visual pass. Cash cap0. Quality failure closes the ledger after one call;
no retry, best-seed search or verification generation. Rounded live account
usage8.52->8.56, credits21.48->21.44, cash charges0/spend cap0. The$0.04 delta
includes associated CPU/builds and rounding, not isolated invoice attribution.
Final container list is empty. Production behavior remains unchanged.

```powershell
python evaluation/audit_object_reference.py evaluation/object-reference-chroma --reference-chroma
python evaluation/render_object_comparison.py --reference-chroma --output review/reference-chroma
python -m unittest discover -s tests
```

Audit exit0 certifies artifact/numerical checks only; `review.json` records
the full visual rejection. Fresh inference requires current live billing,
zero cash cap and a new directory; preparation itself dispatches nothing:

```powershell
python evaluation/prepare_object_reference_chroma.py --output replay/reference-chroma --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_reference_chroma_candidate.py --directory replay/reference-chroma --confirm-credits-only
```

The [comparison](raw-comparison.mp4) and [label-blinded packet](blinded-review.zip)
preserve before/after evidence. Blinding hides labels, not visually inferable
conditions; no independent scores have been obtained. Clean-source verification
uses this machine's existing dependencies; it is not an independent GPU reproduction.

Verification:54 CPU tests pass in17.229seconds from a fresh Git tree extraction, plus the new and prior case artifact/numerical audits. Targeted known-secret/private-media hash scan inspected2587 files/ZIP entries with0 issues; not a universal audit. Only report/status metadata changed after the source check.
