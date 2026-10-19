# Native motion recovery and app integration — October19,2026

**Decision: deploy corrected native motion to the experimental private app.
Overall submission-quality target remains unmet.** Fine fingers fail; exact
likeness, independent normal-speed review and broad generalization are unproved.
Realistic object replacement still fails its earlier scale/lighting gates.

The candidate was frozen before the independent Arm Circles recording was
selected in the [original diagnostic](../native-recipe/FINDINGS.md). Its first
verification lost output after a missing-mask packaging error. That unscored
failure and closed ledger remain unchanged. The new recovery adds only33 white
mask PNGs:103 existing archive entries are byte-identical, including the source,
reference/control tensors. The inference graph and seed are unchanged.

| Case | Provisional frame review | Worker / Comfy seconds | Sampled peak GPU |
|---|---|---|---|
| Independent-recording recovery |33/33 reference-attribute frames;4/4 principal events; dimensions3/4 |86.13 /58.89 |29,109MiB |
| First app integration |Wrapper signature error before inference; no quality verdict |0.257 /none |No useful inference measurement |
| Corrected app integration |33/33 attributes;4/4 events; dimensions3/4; fine-hand defects persist |96.47 /69.59 |29,109MiB |

App CPU control preparation took23.2362seconds. Both successful jobs produce
480×560,33frames,8fps,4.125seconds. All33 raw/composite PNG pairs match exactly
under the full-frame mask; this establishes no outside-region preservation.
The app-returned MP4 bytes, graph and SDK job ID match retained execution.

The app uploads H264 source.mp4, so this second result is a known-footage
integration regression, **not another held-out case**. Relative to the PNG
recovery fixture, source MAE is1.6865/255, pose0.2402 and face3.3117; reference
and mask tensors are exactly equal. No model-component attribution follows.

The frozen gate requires dimensions≥3/4,≥28/33 recognizable reference-attribute
frames and≥3/4 events within±2frames. Curls, beard, connected two-lens glasses,
blue blazer, white shirt and dark trousers persist. Timing, stability, major
anatomy and photorealism provisionally score3/4. Fingers merge/distort during
extension, especially frames8–32; face/glasses proportions differ from reference.
The last two circle-phase events have similar silhouettes and weakly test3D
phase. This is one fixed-camera performer and one previously prepared fictional
reference. Agent frame judgments are not independent professional/normal-speed
approval, exact identity, long-form reliability or Genjutsu parity.

## Implemented and verified

`service.generate` now prepares pinned ViTPose133 whole-body/hand poses and
separate face crops on CPU before native Wan2.2-Animate with the pinned converted
checkpoint, Lightx2v acceleration and relighting adapters. The official Comfy
SDK/proxy remains the executor. Raw source RGB is not the pose input. Existing
seed/prompt/frame controls remain; no automatic portrait completion is added.
Object requests keep the existing VACE worker. No automatic retries/warm GPUs.

A build-order repair happened before dispatch. The first actual integration
exposed a three-versus-four-argument nested wrapper error; its child-call bundle
and inputs were recovered without inference. Regression tests exercise that
exact call and failed-evidence retention. The corrected run used a separately
declared one-attempt budget; the failed ledger was not reset. All36 CPU tests
pass. New local Docker code is not a claimed GPU validation.

The backend was deployed. HTTP smoke checks: unauthenticated401, authenticated
200 with560px maximum side, malformed workload400; no GPU job submitted.
Generation was tested through the same app function on Modal. A fresh browser
generation after deployment remains untested; frontend code was unchanged.

## Reproduce and assess

```sh
python -m unittest discover -s tests -q
python evaluation/audit_native_recovery.py /path/to/private/native-recovery
python evaluation/audit_native_service.py /path/to/private/native-integration-corrected
```

Both offline artifact audits pass; neither certifies visual quality. Private
packets retain frozen/executed source, inputs, raw frames, logs, telemetry,
receipts, reviews and playable comparisons. `modal run service.py::verify_native
--help` describes one-reservation replay with an intact private freeze/request
and live credits-only check. Never reset used ledgers or label replays held-out.

`Dockerfile.native` extends the base local image with pinned controls/assets and
uses the same native functions through local calls, without a Modal account.
The base image retains the legacy Animate2 path. Full local GPU execution and
independent reproduction remain unverified on the4GB laptop; successful cloud
allocation was L40S48GB with64GB requested system memory. Models/hashes are in
`native_recipe_models.py`, pose provenance in `vendor/wan_animate`; the generic
conversion repository's license-declaration gap remains disclosed. No weights,
vendor client code or private human-derived media are redistributed.

Each protocol reserved≤$1 included credits and one900-second GPU call; app
checks also bounded CPU controls to900seconds. Final account billing and clean
source checks are adjacent metadata; account deltas include CPU/build activity
and are not isolated invoices. Out-of-pocket cap remains$0.

[Official rules](https://comfy.org/open-source-higgsfield) were expanded and
rechecked October19: SDK/Router, OSS code/workflows/local instructions, lawful
SFW cleared media,≤2-minute demo and social demo link. The cleared108-second
demo shows older procedural results, not private native tests; an accurate
public-media update is still needed. Formal entry, social publication and
independent review remain pending. No prize/organizer acceptance is claimed.
