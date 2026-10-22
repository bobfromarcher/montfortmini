# Reproduce the montfortmini validation

Scope: existing manual-region object replacement and full-frame character
motion transfer only. Read `PROTOCOL.md`, the retained decision/deviation notes,
and `FINDINGS.md` before interpreting scores. The October 17 evidence archive
contains original recordings, frozen submitted inputs, graphs, masks, raw and
composite PNGs/videos, exact conditioning tensors, logs, environment versions,
GPU samples, model hashes, and a blind review packet. Model weights are not
redistributed. Code is MIT; real footage retains its own CC licenses.

## Analyze the saved evidence without GPU spending

Use Python 3.12+ with FFmpeg/ffprobe on PATH. Analysis was run under Python
3.14.4, FFmpeg 9.0.2 (Gyan full build); complete tool versions are retained.
From the repository root, after extracting the evidence to `validation/`:

```powershell
python -m pip install -r evaluation/requirements.txt
python evaluation/metrics.py validation/runs
python evaluation/paired_analysis.py validation/runs
python evaluation/audit_summary.py validation
python evaluation/package_review.py validation
python -m unittest discover -s tests
```

`metrics.py` writes stage-separated preservation errors, target-color/centroid
diagnostics, flow residuals, and five-time-sample review sheets. `paired_analysis.py`
compares RGB pixels and conditioning arrays, summarizes GPU samples, and exports
all-frame sheets and synthetic endpoint overlays. Endpoint extraction is a
skin/color heuristic with known drawing geometry; ambiguous duplicate arms are
not reliable pose measurements. Color detection can select blue shadows rather
than a blue subject. Neither diagnostic certifies identity, topology or stability.
`audit_summary.py` resolves the rejected fixture's duplicate run name by video
hash; the untouched original ledger remains available.

Open `validation/blind-review/index.html`, score each stage in `review.csv`, and
only then open `unblinding-key.json`. The packet uses shuffled neutral labels.
An independent video professional must review it before calling it independently
validated. Agent scores are separately labeled in `AGENT-REVIEW.md`.

## Rebuild source fixtures

```powershell
python evaluation/download_sources.py --output raw-recordings
python evaluation/build_dataset.py --raw raw-recordings --output rebuilt-data
```

Downloads are hash-checked against `sources.json`; source pages and attribution
are retained. The builder requires FFmpeg's `-display_rotation` input option
and asserts actual rotation side data. An older `rotate` metadata command was
ignored by the local encoder; that invalid fixture/run is retained and excluded.
The saved revision-2 inputs are authoritative for byte-identical replay. Encoding
with a different FFmpeg/libx264 build can change MP4 hashes; do not silently
substitute rebuilt bytes for frozen inputs or call the resulting run identical.

## Repeat inference using included credits only

The existing Modal image pins Comfy and model repository revisions. Runtime
package freezes and five actual model-file SHA256 checks are in the evidence.
Transitive dependencies in the image recipe are not all locked; use the saved
`remote-constraints.txt`/environment record to reconstruct the observed versions,
and verify model hashes and actual Comfy commit before claiming reproduction.
GPU/kernel/library differences can alter determinism. Same-seed equality was
observed only on this tested L40S environment.

Verify the Modal account's included-credit balance and $0 net spend cap first.
Do not add payment methods or paid Genjutsu runs. The CLI acknowledgement is a
manual verification guard, not a billing API. Run one GPU job at a time. Example:

```powershell
python -m modal run evaluation_runner.py --dataset validation/data/dataset.json --output replay/runs --case-ids dev-synthetic-object --profile baseline --variant baseline --seed 42 --confirm-credits-only
```

Replay every row in `validation/experiment-matrix.csv` sequentially using its
case, profile, variant and seed. There are 22 analyzed runs: development cases,
geometry candidate pair, controlled erasure/frozen-driving/reference contrasts,
same-seed repeat, seed 123, eight paired held-out runs, and two exploratory
mask-coverage runs. Each new output ledger is capped at 24 calls / 7,200 measured
worker seconds; this is not an account-wide cap. Existing completed runs are
skipped. Failed runs are recorded and stop the batch; no automatic retries.

`python evaluation/replay.py --evidence validation --output replay/runs` prints
the complete command matrix without running it. Add both `--run` and
`--confirm-credits-only` only after verifying the account budget.

The baseline profile explicitly loads the frozen pre-fix media preparation;
candidate uses current production preparation. The evaluation node is mounted
only in the evaluator image. Reference contrasts use the unchanged production
default prompt and alter reference pixels only. Exact inputs live in
`inputs/conditioning.npz`; stored source PNGs intentionally remain original even
for source-retained/frozen interventions. The original probe manifest's legacy
`target_erased_in_control` flag is inaccurate for source-retained: use
`intervention.json` and the tensor instead. Original manifests are not rewritten.

For the five-file CPU hash audit, add `--audit-models` to the evaluator command.
Do not run Ref2VA-VSA: the reviewed H3 weights are not licensed for this US
deployment, and the patch is not compatible with the Wan graphs. See
`../docs/ref2va-vsa-evaluation.md` for the specific weakness and proposed isolated
test that was not executed.
