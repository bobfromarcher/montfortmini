# Foreground reference-luma correction — October19,2026

**Actual video shade improves while color, size and trajectory gates continue
to pass. Full reference material/lighting quality still fails; no generic object
deployment or held-out generation.** Error reporting is corrected separately.

The previous luma+description candidate retained green17/17 and source scale,
but looked excessively bright/saturated. This contrast changes only foreground
control brightness: gain0.741566, computed from original reference/source
foreground median encoded-RGB luma. The same gain applies to all frames with
5×5,sigma1 feathering. The source/reference PNGs, edit masks, positive prompt,
model, seed42,20steps,CFG5,uni_pc/simple,shift8,strength1,480×272,17frames,8fps
remain unchanged. Graph node6 selects the new control loader; annotations and
the derived source-control tensor are explicit inputs.

The control function accepts foreground masks independently of their colors.
This development fixture uses a **source-only annotation oracle**: largest
high-saturation yellow component within the original edit mask, exterior
contour fill; largest green reference component. No generated pixels guide
annotation/gain selection. This is not generic segmentation. A passing result
would still need general input preparation before app promotion. The edited
foreground target mostly has image-space drift; the bee pushes another ball.
Arbitrary replacement shapes, contact/occlusion and population success are unproved.

The first attempt failed before sampling: OpenCV was present in the development
environment but absent from the GPU image. All evidence and its closed ledger
remain in [object-reference-luma-failed](../object-reference-luma-failed).
A separately bounded corrected attempt replaced the Gaussian with NumPy and
added CPU preflight in the actual inference image. Original input ZIP and graph
bytes remain exact; maximum control change is5.96e-8, below the explicit2e-7
float32 instrumentation tolerance. Gain is unchanged. This was a post-failure
technical recovery plan, not preplanned before the first call and not a seed
reroll. The original protocol was closed rather than reset.

The real-container preflight loaded the installed custom-node file, verified
its hash against the root source, and reproduced the frozen control. During
Comfy execution, the node retained its exact returned control/mask/reference
arrays and gain. Runtime/source/archive/graph checks pass; outside control RGB
is exact. Source snapshots preserve both the failed and corrected implementations.

| Measurement | Previous luma+description | Reference-luma correction |
|---|---|---|
| Green raw/composite frames |17/17 |17/17 |
| Target/source color-area median |1.106 |0.955 |
| Centroid error/image diagonal |0.004337 |0.003609 |
| First-frame foreground median luma |0.640 |0.536 |
| Raw outside-region MAE/p95 |2.345/7 |2.368/7 |
| Encoded outside-region MAE/p95 |1.770/4 |1.771/4 |
| Composite outside-mask max error |0 |0 |

Reference foreground median luma is0.449. The first-frame generated green RGB
median changes7/222/2→5/187/6; reference34/145/49. The shade is closer but strong
saturation/material mismatch remains. These segmentation-dependent summaries
are exploratory, not calibrated reflectance, new thresholds, or proof of cause.
All17 raw frames were inspected. Conservative provisional scores for raw and
composite: coarse reference attributes3,motion3,stability3,shape3,scene material/
lighting2. Full gate_pass=false; independent professional/normal-speed review
is pending. Numerical gates all pass under the unchanged prior rubric.

Failure worker13.337seconds,13 GPU samples, sampled peak440MiB; no diffusion
sampling occurred. Corrected worker63.278seconds, Comfy graph44.77seconds,
62 GPU samples, sampled peak11,906MiB. Host peak RAM is unavailable because the
cgroup file was missing. CPU-preflight duration was not separately measured.
Model remains VACE1.3B pinned to Comfy-Org/Wan_2.1_ComfyUI_repackaged@
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d; Comfy commit
5cc4b870094c89090db54bd8d12649dcaf89f2ba,SDK0.5.0/proxy0.1.6.
Corrected call fc-01M5B9ENS5SN6KVP1ERX07SWJH, SDK
16343d27-c967-4bff-8d7a-cdff60e03f0d; original failure
fc-01M5B98GG813SAE967YHJFMPRR. Exact receipts/logs are retained.

Both development protocols cap one GPU call at660seconds/$0.75 included each.
The cycle planning ceiling is$3 included, cash0 and at least$2 verification
reserve. Quality failure closes further inference; no verification/integration
generation follows. Billing observations and final account totals accompany
the private evidence; account deltas include builds/CPU and rounding, not
isolated invoices. No claim about Genjutsu's proprietary backend is made.

A separate product repair retains the bounded Comfy execution cause when an
SDK job returns too few frames. The jobs API identifies missing dependencies
as a server configuration error rather than suggesting a shorter input clip.
It does not expose a traceback or automatically resubmit. These post-inference
error-reporting edits do not change the observed video's graph or sampling;
the original executed sources remain frozen in the run snapshots.

```powershell
python evaluation/audit_object_reference.py evaluation/object-reference-luma --reference-luma
python evaluation/render_object_comparison.py --reference-luma --output review/reference-luma
python -m unittest discover -s tests
```

The offline audit's exit0 certifies artifact/numerical checks only; review.json
retains the full visual rejection. Fresh reproductions require current observed
$LiveUsage/$LiveCredits, zero cash cap and a new directory. The preparer never
dispatches inference; the controller runs CPU container preflight before one GPU
reservation and rejects an existing ledger or changed source/input hashes.

```powershell
python evaluation/prepare_object_reference_luma.py --output replay/reference-luma --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_reference_luma_candidate.py --directory replay/reference-luma --confirm-credits-only
```

The next unresolved issue is reference chroma/material fidelity, followed by
generic foreground preparation and genuinely unseen verification. More compute
or a larger checkpoint is not yet demonstrated necessary. Both failures and
improvements remain inspectable; unmet quality is not presented as success.
Media attribution: [SOURCE-LICENSE.md](SOURCE-LICENSE.md). Code MIT; source and
bee-derived media CC BY4.0. Overall competition readiness remains unmet.

Final verification:51 CPU tests pass in27.90seconds from a fresh Git source extraction; combined artifact checks took39.85seconds. Targeted known-secret/private-media scan2359 files/ZIP entries found0 issues (not a universal audit). The error-reporting repair is deployed; live unauthenticated/authenticated/invalid-request checks return401/200/400 without a generation. Offline replay of the actual retained Comfy failure confirms the dependency cause reaches the safe API message. No inference algorithm from this study is promoted. Rounded account usage8.47→8.52, remaining included credits21.48, cash charges/spend cap0: about$0.05 account delta, including the failed call, corrected call and associated CPU/builds, not isolated invoices. The [label-blinded packet](blinded-review.zip) contains both before/after conditions with blank review sheets; no external reviewer has scored them.

Final Modal container listing is empty; both experiment calls have completed.
