# Reference and motion recovery study — October 18, 2026

The frozen experimental cascade improved a difficult development recording but
**failed the new independent-recording identity test**. It is not the deployed
app path. The realistic quality target remains unmet. The previous VACE object
scale/lighting failure also remains; this motion study does not repair it.

The shipped `service.py` still uses the previously documented VACE/Animate2
graphs and preprocessing. Experimental commands below use `cascade_candidate.py`.
They do not change the hosted app. No Genjutsu implementation details were
observed beyond its UI, submitted inputs and output; internal-model explanations
remain hypotheses.

## What changed, and what was actually learned

Headshot and standing reference inputs lost the seated source performance.
Paired development controls retained identical source pixels, masks and video
graphs while replacing only the prepared reference. A source-pose-matched
reference restored seated framing and visible hand/menu movement. Stronger pose
conditioning and an alternate base-model recipe did not solve the original
framing failure. This supports a reference-composition failure on that recording;
it does not establish one universal cause of poor motion transfer.

The open preparation candidate uses FLUX.2 Klein4B (native four-step distilled
recipe), Qwen-Image-Edit-2511 (native 40-step base recipe) and the existing
10-step Wan Animate2 distilled video graph, in that order. Klein kept scene
composition but changed fine facial structure. Qwen alone kept a closer face but
lost clothing and introduced a phone. Appending a target caption recovered
clothing while changing camera/background composition. Qwen refining the saved
Klein frame gave the most useful development result. Changing only the CLIP
appearance input, or reference strength from 1.0 to 1.3, offered no persuasive
visual improvement. All alternatives and failures were retained.

The new CC0 recording and an original fictional adult reference were selected
before candidate inference; the candidate code was frozen before its first run.
That test completed all three stages in **579.95 worker seconds**, producing
33 frames at 480×560 and 8fps. Sampled peak VRAM was **30,654MiB** on L40S.
Klein retained the source headwrap, Qwen dropped the reference glasses and made
the face stylized, and the video therefore animated an already wrong identity.
The failure is visible before video inference. Low lighting, face size in the
reference and source-accessory dominance are possible explanations, not isolated
causal findings. No tuning or reroll followed this held-out result.

The development cascade video used cached reference-stage outputs: its 261.14s
worker time is **video only**, not fresh end-to-end latency. Its sampled peak
VRAM was 29,852MiB. Minor face, shirt-pattern and geometry drift remained.
These visual assessments are by the coding agent; independent professional
ratings have not been supplied.

## Acceptance and limitations of the evidence

The retained [rubric](recovery/RUBRIC.md) requires every applicable dimension at
least 3/4, recognizable defining attributes in at least 28/33 or 14/17 frames,
and no duplicate limbs, collapsed subject or extra subject. Face geometry,
reference attributes, source motion, temporal stability, anatomy and realistic
appearance are separate judgments. Inspect every native frame, then play the
clip at 8fps. The fresh case fails reference fidelity regardless of the motion
score. Signing semantics are outside the assessment.

The confirmation protocol specified source-gesture order and a two-frame timing
tolerance, but did not freeze four fully timestamped landmarks. A formal
three-of-four timing pass cannot be claimed retrospectively. Broad gesture
recognizability and visible failures can still be described; future timing
claims need source-only timestamp annotations frozen before output review.

Raw and composited PNG pixels match exactly in the new motion result because
the mask covers the full frame. That is not source-background preservation.
The audit separately decodes all three MP4s and verifies frame count, dimensions
and declared rate. Hardware allocation (64GiB RAM) is not a measured physical
RAM peak; cgroup readings were unavailable. One independent real recording
cannot establish a success rate. The known synthetic regression is development
evidence, never a second independent held-out recording. It completed in506.22s
at576×480,17frames,8fps, with30,910MiB sampled peak VRAM. It reproduced broad
arm raising but changed flat artwork into a different rendering style, invented
a bedroom background, and lagged/incompletely lowered the arms. It does not
support production promotion. The baseline comparison is a complete-pipeline
regression check: input uploads match, but prepared source/mask dimensions,
reference pixels and graph nodes7/17 differ. It is not a one-factor ablation.

## Reproduce without generation charges

Install Python dependencies from `evaluation/requirements.txt` and FFmpeg.
With an extracted evidence run, execute from the repository root:

```sh
python evaluation/audit_cascade.py --run /path/to/extracted/run --output audit.json
python evaluation/audit_cascade.py --run /path/to/candidate --compare /path/to/control --output paired-audit.json
```

The audit reads images, graphs, conditioning, recorded resources and hashes;
it performs no downloads or inference and does not assign perceptual scores.
Full private evidence contains the original media, masks, conditioning tensors,
raw/composited PNGs, MP4s, stage graphs, SDK job receipts, logs and environment.
Do not confuse public metadata with a complete original-media evidence archive.

Public metadata lives in [recovery](recovery/), including the frozen code
hashes, independent case selection, source metadata, model/stage provenance and
technical audits. Publicly cleared synthetic examples remain in
`evaluation/quality/samples/`. The source's copyright declaration is CC0, but
performer likeness permission for promotional redistribution was not established;
its footage and derivatives are excluded from the public repository and demo.
Original private development portraits/footage and the Genjutsu result are
also excluded. The included `reference-original.png` is an original fictional
adult input created using the assistant's included image tool; that tool was
not used in the selected inference pipeline. An earlier externally prepared
frame was a diagnostic control only, not an open-model implementation.

## Exact optional GPU replay

This requires your own authorized compute. Never assume another person's credits
or a local 4GB GPU can execute it. Allow a 48GB GPU, 64GiB worker RAM and
substantially more model disk than the default app (roughly 80GB of weights).
The wrapper pins repository revisions and verifies weight SHA256 values during
image build. Model identities are in `anchor_workflow.py`,
`qwen_anchor_workflow.py` and `motion_model_config.py`; all selected model cards
declare Apache2.0. App code remains MIT. Upstream model terms are retained.
No H3/Ref2VA-VSA inference was performed: its required model is incompatible
with this runtime and its applicable licensing was not suitable for this US
setup. It is not an evaluated solution to the observed failure.

Reconstruct the historical research case (31MB public-source download; no GPU):

```sh
python evaluation/prepare_confirmation.py --output /path/to/new-reconstruction
```

The reconstruction records the original and derived hashes plus FFmpeg version.
An exact original SHA mismatch stops processing; encoded clip bytes may differ
across FFmpeg builds and are reported explicitly. This is the already observed
case, not a new held-out test.

For a JSON case file with relative `video`/`reference` paths, `mode`, `prompt`,
and `frames`, run the frozen experimental wrapper explicitly:

```sh
python -m modal run --detach cascade_candidate.py --cases /path/to/cases.json --case signer --output /path/to/new-result --frames 33 --confirm-credits-only
```

There is no implicit free-generation guarantee. Confirm the provider's included
credit balance and $0 cash cap yourself first. The recorded study's phase budget,
pre-call revisions and stopping rules are preserved in the protocol files;
no further discovery calls were permitted after its eighth final attempt.

Full independent GPU reproduction and blinded professional review remain
outstanding. The available laptop cannot execute these models locally. Clean
checkout checks validate setup/imports/CPU analysis, not another person's
independent inference or a successful realistic-quality result.

## Resource accounting and final decision

Eight GPU attempts in this editor/confirmation phase completed successfully, totaling **2986.80 measured worker seconds** (49.78minutes), below3600. Earlier recovery-phase infrastructure failures and reservations remain in the separate private ledger; they are not silently removed from accounting. The final attempt used an unchanged frozen render function with a tighter660sec ceiling. Original frozen runtime source hashes still match. No further GPU calls are permitted in this study. All experimental apps are stopped and the final container inventory is empty.

The end dashboard snapshot reports5.62 total included-credit usage while its usage breakdown reports6.1996. Against the3.38 phase baseline, the displayed delta is2.24, or up to2.8196 using the higher value conservatively. These are delayed/inconsistent provider UI totals, not an exact per-run invoice. Cash spend and cash cap both remain **$0**. The final conservative total remains below the original6.23 overall stopping threshold. Provider-rate estimates do not replace measured billing.

The candidate remains research-only. The working default app, public source/demo, setup instructions and submission drafts are prepared, but this is not a successful realistic-fidelity result, a guaranteed eligible entry or an award claim. See `submission/REQUIREMENTS-AUDIT.md` for the official checklist and remaining entrant actions.
