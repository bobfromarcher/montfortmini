# Native recipe diagnostic — October 19, 2026

**Decision: development improvement demonstrated; generalization unverified;
not promoted to the app and not submission-ready.**

The actual recast video now provisionally passes the development rubric. The
reserved independent-recording run completed inference but failed during
compositing because our fixture omitted PNG mask files. Its video was not
retained, so it has **no perceptual-quality verdict**. The three-call cycle is
closed; there was no corrected-fixture GPU retry.

## Consequential change and observed result

The old base-only approximation differed from the official native Comfy recipe.
This diagnostic uses its converted checkpoint, Lightx2v acceleration adapter,
relighting adapter and six-step Euler/simple sampling, CFG1, shift8. A generic
prompt replaces the old appearance caption. This is a recipe-bundle comparison:
it does not isolate the contribution of each changed component or the prompt.
Our 480×560,33-frame,8fps workload also differs from the full official template's
dimensions, lengths and continuation. It is not a recovered Higgsfield graph.

| Case | Provisional visual result | Worker / graph seconds | Sampled peak GPU |
| --- | --- | --- | --- |
| Source-character oracle | 4/4 event matches; coherent visible attributes. Shadowed face limits identity judgment. | 78.51 /53.81 | 29,082MiB |
| Frozen fictional reference | 4/4 event matches;30/33 frames clearly retain reference attributes; all anchored dimensions3/4. Hand blur and facial/glasses detail drift remain. | 82.23 /55.50 | 29,109MiB |
| Independent arm-circles recording | Technical failure after inference. Quality unknown. | 80.74 /54.45 | 29,114MiB |

The recast no longer shows the retained baseline's headwear/extrusion defect.
Source,mask,pose and face tensors are identical between oracle and reference
runs; only reference pixels change. Both successful videos have33/33 raw and
composited frames exactly equal under a full-frame mask. This establishes no
outside-region preservation or realistic object-swap improvement. Source facial
RGB does not inevitably cause the prior artifact: the new development recipe
retains those same controls without that defect. Its interaction with other
components is still unresolved.

Ratings are agent visual judgments, not independent professional review. The
source-character oracle does not establish recasting. Development success is
not generalization or Genjutsu parity.

## Frozen test and technical failure

Candidate code, graph and reference were frozen before selecting new footage.
The selected [Arm Circles recording](https://www.dvidshub.net/video/551356/arm-circles)
is identified by DVIDS as public domain, by Capt. Matthew Holfinger, U.S. Marine
Corps Training and Education Command, VIRIN170914-M-JT909-001. Original SHA256:
`b44f9ea5707c091863755a9c65231e06a3a790219bbaa41eb0be04c1b622a3e2`. Source-only selection is9.5–13.5s,
33samples at8fps, crop(256,16,480,560), no resize. The latter circle-phase events
have similar silhouettes; this short test is weak evidence of precise3D phase.
A different power-throw recording was rejected before inference because people
overlap and camera cuts conflict with the frozen single-person preparation.

The input NPZ contained its full-white mask tensor, but33 PNG masks required by
the compositor were absent. Logs confirm54.45seconds of Comfy execution before
`FileNotFoundError` for `masks/0000.png`. The ephemeral worker's failure bundle
did not retain its generated frames. This is an avoidable fixture/retention
defect, not evidence of a model-quality failure or an unseen pass.

The exact failed archive now fails offline preflight. Adding only the missing
white masks produces a separately hashed corrected archive that passes that
check. The original archive/freezes remain unchanged. The corrected runner checks
all required frame artifacts before GPU dispatch and preserves available model
images if later compositing fails. Three regression tests cover this defect;
the complete CPU suite passes30tests. The actual three runs used the original
17-module source snapshot; repaired source is a later revision, not retroactively
claimed as executed.

A clean Git-source extraction also passes30tests in20.612seconds using the
existing environment on the same machine. All106 Python files match the
metadata-preserving archive; frozen protocol/JSON original bytes were checked.
This is not independent GPU reproduction or a fresh dependency installation.

## Reproduction, spending and release limits

Exact model repositories, revisions, sizes and hashes are in
`native_recipe_models.py`; the private packet retains executed-source.zip,
inputs, outputs, graphs, logs, telemetry and freezes. Check retained evidence:

```sh
python evaluation/audit_native_recipe.py /path/to/private/native-recipe
python -m unittest discover -s tests -q
python evaluation/init_native_recipe_reproduction.py --help
```

The audit exits1 for this closed evidence set because verification failed; this
is expected. The initializer makes a new budget/freeze directory from the
private packet, including repaired masks. It starts no inference. Use
`modal run native_recipe_candidate.py --help` for replay; oracle/reference
review files must pass before each next stage. Replaying these known recordings
is reproduction, never a new held-out test. Independent GPU reproduction and
professional review remain outstanding.

Three L40S calls consumed241.4823worker seconds; CPU whole-body test preparation
took28.4779seconds. Displayed account usage increased7.93→8.14, credits
22.07→21.86, cash spend/cash cap stayed$0/$0; observed account delta$0.21 is not
an isolated invoice. The cap was$2 included credits and2700reserved GPU seconds.
Final container inventory is empty.

The converted FP8 model card declares Apache2.0. The Kijai general conversion
repository has no global license declaration; its README attributes the Wan
weights and the I2V adapter to their Apache2.0 upstreams. That declaration gap is
retained rather than called cleared. No weights, proprietary Higgsfield code or
human-derived evaluation media are published. DVIDS publicity/privacy rights are
not waived; human footage and derivative review videos remain private. The
existing public demo does not demonstrate this new result. The deployed motion
path and realistic object-swap limitation remain unchanged. A successful
corrected-fixture verification, app integration/validation, publication-cleared
demonstration and independent review are still required.
