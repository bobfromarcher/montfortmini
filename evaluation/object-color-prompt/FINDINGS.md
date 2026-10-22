# Two-color-word ablation — October 21, 2026

**Rejected: removing two “green” words turns the target beige in all17 frames,
despite unchanged reference and color-control inputs.** This matched run shows
strong sensitivity to color wording, not a successful reference-fidelity fix.

Before running, the planned broader descriptor deletion was narrowed to removal
of only the two `green` occurrences. `smooth`, `solid`, size, light, scene and
motion descriptions remain. Removing material words too would have confounded
the comparison. The complete input ZIP is byte-identical to the retained
reference-chroma baseline; node4.inputs.text is the sole changed graph field.
The reference, source-derived chroma/luma control, foreground/edit masks, negative
prompt, model, seed42 and sampler settings remain fixed. The frozen
[protocol](PROTOCOL.json) lists predictions, competing interpretations and stops.

Useful extra data were added before the new output existed: all17-frame RGB
medians, encoded-luma quantiles, saturation, RGB/sum chromaticity distance and
adjacent-frame median-color variation. The source/reference foreground masks
are eroded inward2px and fixed independently of generated colors. Raw and
composited outputs are assessed separately. Results are executable JSON/CSV,
with per-frame paired differences. No extra inference, model or output color
correction is used. Pre-run self-comparison checks the metric path on actual
retained baseline media; actual-container preflight checks executed controls.

| Measurement | Two green words | Green words removed |
|---|---:|---:|
| Green raw/composite frames |17/17 |0/17 |
| Fixed-ROI median saturation, /255 |255 |115 |
| Fixed-ROI median encoded luma |0.5441 |0.5166 |
| Fixed-ROI median chromaticity distance to reference |0.4491 |0.4083 |
| Median adjacent RGB step, /255 |1.866 |1.732 |
| Maximum adjacent RGB step, /255 |4.243 |5.385 |
| Raw outside-region MAE/p95, /255 |2.312/7 |2.374/7 |
| Encoded outside-region MAE/p95, /255 |1.770/4 |1.771/4 |
| Composite PNG outside-mask maximum error |0 |0 |

The added diagnostics expose a failure of metric-only selection: color distance
is lower in15/17 paired frames even though the new target is visibly beige.
First-frame fixed-ROI RGB is162/126/89; reference core35/148/50. Lower saturation
and distance do not establish the right reference subject. Scores are not new
gates and were not used to rescue this failed video. The earlier first-frame
green-selected medians use a different region and should not be substituted for
these all-frame fixed-region statistics.

All17 raw frames were inspected: a continuous spherical target remains, but
defining color and smooth shaded reference appearance are lost. Provisional
raw/composite scores: reference1,motion3,stability3,shape3,material/lighting2.
Raw/composite target PNG pixels match exactly; compositing does not repair the
reference. Preservation passes. Green-area scale/centroid proxies are
unavailable because the target is not green; their failure does not demonstrate
geometric collapse. Artifact invariants pass and full quality fails.
Independent normal-speed professional assessment remains outstanding.

The pair supports a practical conclusion: this recipe's reference/control inputs
do not maintain the desired green appearance when the two explicit color words
are removed. It does not prove that reference conditioning is absent or identify
whether remaining scene/material wording, reference attention, training or model
capacity explains the failure. Before another prompt sweep or model replacement,
the next discriminating question is reference-branch sensitivity with text and
reactive control held fixed. That experiment is not run under this closed budget.

One known development recording/seed, fixture-specific foreground oracle,
correlated frames, no GPU repeatability calibration. Source-anchored ROIs may
include background when geometry drifts. Lighting/material differences confound
reference distances. Adjacent median-color changes include source motion/light;
they are not motion-compensated flicker scores. The edited target mostly drifts
in image space; the bee pushes another object. No contact, occlusion, arbitrary
replacement, character-motion generalization or Genjutsu backend claim follows.
The retained runtime manifest's generic `target_erased_in_control=true` field
is inaccurate for this research loader; exact runtime tensors and graph show
retained source geometry/luma/reference chroma. The original manifest is preserved.

Worker47.367seconds; Comfy graph24.38seconds including loading;46 GPU samples,
sampled peak11,905MiB L40S. CPU-preflight end-to-end client interval10.377seconds,
including startup/transfer; host peak RAM unavailable (missing cgroup path).
Modal call fc-01M5FDTW89Q891P0075SBTE7NS, SDK job
e6fe3015-0751-4589-a5a3-ae678cce4041. VACE1.3B model revision
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d, Comfy
5cc4b870094c89090db54bd8d12649dcaf89f2ba, SDK0.5.0/proxy0.1.6 unchanged.
Exact original media, prompt diff, workflow, executed controls, source/analysis
snapshots, receipts, logs and resources are retained. Code MIT; source and
bee-derived media CC BY4.0 with [attribution](SOURCE-LICENSE.md).

One development call capped660seconds/$0.75 included; total cycle ceiling$2.25
reserves$1.50 for verification only after a full visual pass, cash0 and at least
$2 remaining. Quality failure closes the ledger after this one call. No retry,
seed search, new unseen test, production promotion or deployment follows.

```powershell
python evaluation/audit_object_reference.py evaluation/object-color-prompt --color-prompt
python evaluation/object_color_diagnostics.py --inputs evaluation/object-color-prompt/inputs.zip --baseline evaluation/object-reference-chroma --candidate evaluation/object-color-prompt --output review-color.json
python evaluation/render_object_comparison.py --color-prompt --output review/color-prompt
python -m unittest discover -s tests
```

The audit intentionally exits1 for failed color/derived proxies while all
artifact invariants pass. Do not label this a technical inference failure.
Fresh inference requires live billing and a new directory; preparation is CPU
only and the controller rejects old ledgers or changed frozen files:

```powershell
python evaluation/prepare_object_color_prompt.py --output replay/color-prompt --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_color_prompt_candidate.py --directory replay/color-prompt --confirm-credits-only
```

Live billing: usage8.56->8.59, included credits21.44->21.41, cash charges/spend cap0; approximately$0.03 account delta including CPU/builds and rounding, not isolated invoice.

Verification:56 CPU tests pass in18.263seconds from a fresh Git source extraction; new artifact invariants and prior-case artifact/numerical regression pass. The new quality-proxy failure is expected and separate. Targeted known-secret/private-media scan2822 files/ZIP entries,0 issues; not a universal audit. Final container list empty. Label-blinded packet retains both conditions with blank review forms; no external review received.
