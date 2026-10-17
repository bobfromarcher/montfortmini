# Reproduce the quality follow-up

Read [the findings](quality/FINDINGS.md), [frozen rubric](quality/RUBRIC.md), and
[decisions/deviations](quality/EXPERIMENT-DECISIONS.md) first. The realistic quality
target was not met. Only the SDK status/receipt repair was shipped; the global
reference-cover candidate was rejected. Historical profile `production` means
the default-prompt cover experiment, not released behavior. `candidate` always
uses the frozen experimental preparation, independently of the production file.

## Offline assessment, without GPU charges

Install `evaluation/requirements.txt`; FFmpeg/ffprobe must be on PATH. Saved
public samples contain original submitted bytes, actual float32 conditioning,
source/masks/raw/finished PNGs, MP4s, graphs, manifests, logs, environments and
GPU samples. Code is MIT; media attribution is in `quality/ATTRIBUTION.md`.

```powershell
python -m pip install -r evaluation/requirements.txt
Copy-Item evaluation/quality replay-quality -Recurse
python evaluation/quality_analysis.py replay-quality --runs-name samples
python -m unittest discover -s tests
python -m unittest discover -s evaluation -p test_reference_candidate.py
```

This recomputes the **three publicly cleared samples**, not the combined
14-run historical table. Work on a copy so the original aggregate remains
available. Color/centroid/preservation checks and the fixture-specific hand
heuristic cannot certify appearance or motion. Its source/target skin-color
overlays are exploratory and must be inspected.

Open `quality/blind-review/index.html`. Score every frame of raw and finished
videos in the blank CSV using RUBRIC.md, before opening the separate
`public-unblinding-key.json`. Conditions may be visually identifiable; labels
are blinded, not guaranteed experimenter/reviewer blindness. Agent scores are
separately labeled. Independent professional review remains pending.

The private research archive contains the full 14-run packet and Genjutsu media;
it is not a public asset bundle. No public likeness clearance is asserted for
those files. The public packet contains original art and attributed CC-BY bee
footage. The US Army recording has US public-domain copyright status, but is
excluded from public submission media because no model release is established.

## Rebuild the new test inputs

```powershell
python evaluation/download_quality_sources.py --output quality-originals
python evaluation/build_quality_tests.py --raw quality-originals --output replay-inputs/new-tests
```

The second command writes `replay-inputs/quality-cases.json`, with paths relative
to that file. It builds two original synthetic cases and excerpts two independent
recordings. Synthetic scenes share procedural assumptions; the real-motion
target is illustrated, so this is not a new photorealistic identity holdout.
The saved bytes/hashes are authoritative. A different FFmpeg/Pillow build can
change encoded bytes; investigate hash differences instead of calling them exact
reproduction. Do not publish newly built human-source media without clearance.

## Repeat inference only against verified included credits

Use your own Modal account, verify remaining credits and a $0 net-spend cap,
and run one job at a time. The CLI flag is an acknowledgment, not a billing API;
caps are per output ledger, not account-wide. No weights are stored in this repo.

```powershell
python -m modal run fidelity_runner.py --cases replay-inputs/quality-cases.json --output replay-results/runs --case new-synthetic-object --profile baseline --seed 42 --confirm-credits-only
```

Profiles: `baseline` is retained reference fitting; `candidate` is the rejected
center-cover preparation. Both replay with the repaired SDK. Frozen baseline,
pre-cover, candidate and historical SDK modules preserve the original recipes.
The final SDK also emits the confirmed job ID to platform logs before polling,
so the receipt survives loss of an ephemeral container. The frozen polling SDK
matches the five post-repair inference runs before that logging-only addition.
Early development used the old 30s SDK transport; exact historical transport
requires its frozen module in a disposable checkout, and can time out again.
Do not resubmit an ambiguous POST. A known job receipt is saved before polling.

The original follow-up budget ended at 14 completed generations, one polling
failure and one reserved runner failure, then stopped. Repeating inference
consumes your account's credits. Transitive GPU dependencies were recorded at
runtime but are not all locked in the build recipe. GPU/library differences may
change pixels; no cross-machine bitwise determinism is claimed.

## Rebuild the demonstration

```powershell
python evaluation/make_demo.py --samples evaluation/samples --ui submission/demo-assets/workbench.png --output rebuilt-demo
```

The 108-second video uses actual original procedural examples and a retained
failure. Resizing, caption layout and repeated playback are disclosed; there is
no model-frame repair or interpolation. System fonts are not redistributed.
Clean frontend install/typecheck/build, local cookie sign-in and read-only
backend status were verified. Full GPU Docker execution and independent
clean-machine inference remain unverified on the available 4GB laptop.
