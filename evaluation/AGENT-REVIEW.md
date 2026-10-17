# Preliminary agent visual review

This is **not independent professional validation**. Review used the reference,
prepared source, five-time-sample raw/composite sheets, and complete 17-frame
raw sheets for the principal successes/failures. Scores are ordinal judgments,
not calibrated probabilities. The blind packet contains blank reviewer forms.
Raw and composite subject scores are the same here because compositing retains
raw pixels inside the object selection. Their background results differ and
must be read separately in metrics.json. Motion cases use a full-frame mask,
so their raw and composite pixels are identical.

| Case / condition | Raw fidelity / motion / stability (0–4) | Composite fidelity / motion / stability | Interpretation |
|---|---|---|---|
| Development synthetic object, seed 42 | 4 / 4 / 4 | 4 / 4 / 4 | Single blue sphere follows the prescribed path; minor shadow/edge differences. All 17 frames retain it. |
| Same seed repeat | 4 / 4 / 4 | 4 / 4 / 4 | Raw RGB frames exactly equal the first run. |
| Seed 123 | 3 / 4 / 3 | 3 / 4 / 3 | Sphere retained throughout; shape/shadow and some background traces change. |
| Held-out synthetic object, both profiles | 4 / 4 / 4 | 4 / 4 / 4 | Single green sphere, reversed trajectory, 17/17 frames. Profiles are pixel-identical. |
| Source retained instead of erased | 1 / 4 / 4 | 1 / 4 / 4 | Blue cube remains: recoloring is not silhouette replacement. Diagnostic intervention. |
| Default prompt + blue reference | 1 / 3 / 3 | 1 / 3 / 3 | Rounded beige object with blue shadow; reference color not reproduced. |
| Default prompt + green reference | 1 / 3 / 3 | 1 / 3 / 3 | Yellow/beige rounded disk; requested green absent. |
| Default prompt + gray reference | 0 / 3 / 2 | 0 / 3 / 2 | Unrequested face-like patch; no reference subject. |
| Development synthetic motion | 4 / 3 / 4 | 4 / 3 / 4 | Orange hair/blue shirt, recognizable rising arm, modest timing/position lag. 17/17 subject frames. |
| Frozen driving frames | 4 / 0 / 3 | 4 / 0 / 3 | Reference appearance retained; arm remains largely lowered. Diagnostic intervention. |
| Held-out synthetic motion, both profiles | 2 / 1 / 1 | 2 / 1 / 1 | Original lowered arm remains while a second ghost arm appears from roughly frame 3 onward; fails topology/stability. Profiles pixel-identical. |
| Development real object, registered mask, baseline | 1 / 2 / 2 | 1 / 2 / 2 | Stretched geometry; metallic remnants. Mask misses part of original target. |
| Development real object, registered mask, candidate | 2 / 2 / 3 | 2 / 2 / 3 | Correct display aspect and rounder output; original metal remains outside selection. Not a complete replacement pass. |
| Development real object, coverage control, baseline | 1 / 3 / 3 | 1 / 3 / 3 | Full target erased but replacement is an elongated capsule. |
| Development real object, coverage control, candidate | 2 / 3 / 3 | 2 / 3 / 3 | Round blue disk; reference shading/volume is weak. Geometry improves, fidelity remains partial. |
| Development real motion | 3 / 2 / 1 | 3 / 2 / 1 | Character recedes but remains front-facing while source walks away; severe background ghosting at frames 14–16. |
| Held-out real object, both profiles | 2 / 0 / 2 | 2 / 0 / 2 | Oversized green object does not track the small bouncing target. Target leaves the static mask; selection confounds model-only interpretation. |
| Held-out real motion, baseline | 2 / 1 / 2 | 2 / 1 / 2 | Upright head with unnaturally stretched arms during floor phase; stripe artifacts. |
| Held-out real motion, candidate | 3 / 3 / 3 | 3 / 3 / 3 | Folded-to-standing phase recognizable; 5/5 sparse phase samples agree, versus 2/5 baseline. Exploratory: annotations were late and prompt says jumping jacks while source crop is a burpee. |

The clean synthetic object cases and development wave satisfy the preliminary
agent visual gates and their numerical gates. This does not make them
independently validated. No aggregate success percentage is warranted: repeated
runs and ablations are not independent cases, and real fixtures have documented
selection/action confounds. Inspect all raw PNGs and videos before judging.

The endpoint detector is a disclosed color/skin heuristic. Its first analysis
mistakenly allowed dark trousers into torso alignment; it was corrected to use
the known synthetic torso ROI and exported endpoint overlays. That measurement
repair changed no inference inputs, production code, or acceptance threshold.
Duplicated/ghost arms make a unique endpoint ambiguous; the held-out motion
fails visually regardless of which endpoint is chosen.
