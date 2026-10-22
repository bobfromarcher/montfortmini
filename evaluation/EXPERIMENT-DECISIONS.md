# Decisions before held-out inference

The corrected, tagged development fixture independently decodes to 480x360
with ffmpeg, while the frozen application prepares it as 352x480. Its generated
replacement is elongated and develops metallic patches. The defect is that
ffprobe encoded dimensions were used to plan the resize while ffmpeg applies
display rotation before resizing. This is a confirmed geometry bug; the degree
to which it causes each generative artifact remains a hypothesis.

The only candidate production change is `media_pipeline.py`: read and honor
display-matrix or legacy quarter-turn rotation before computing dimensions,
letterboxing and mask coordinates. The sampler, models, prompts and inference
graphs remain unchanged. Nine tests pass, including an actual tagged video
with a known red region and independent metadata assertion. Hashes are in
`candidate-freeze.json`. Freeze this candidate before held-out generated output
inspection. Do not tune against held-out results.

Development motion already exposes a separate limitation: on real walking
footage, the generated illustration changes scale and shows background ghosting
at the final frame. No model-quality correction is claimed from the geometry
repair alone. Investigate the driving/reference contribution with controls;
retain this failure if it persists.

## Causal group registered before execution

- Object `source-retained`: unchanged source/mask/prompt/seed, but disable target
  erasure in the conditioning tensor. This tests the erasure mechanism.
- Motion `frozen-motion`: repeat the first driving frame in the model input.
  Source evidence remains original. This tests the temporal driving signal.
- Object reference contrast: submit the unchanged production **default** prompt
  (blank user prompt) with blue-ball, green-ball, and neutral-gray references.
  This removes the explicit color/shape descriptions that confound attributing
  the earlier blue sphere to reference guidance. Only reference pixels differ
  across this group, with seed 42 fixed. Report input/conditioning hashes.
- Repeat the explicit-prompt development object at seed 42 and seed 123 to
  separate same-seed reproducibility from seed sensitivity.

These controls are diagnostic interventions, excluded from production case pass
rates. Metrics on controls are not interpreted as normal feature acceptance.
The registered budget remains 24 calls / 7,200 worker seconds; the rejected
fixture run and initialization failure still count toward consumed resources.

## Source-only mask and action audit (before held-out output inspection)

The registered development metal-sphere rectangle starts at x=.32 while the
source sphere extends to approximately x=.23. Preserve this undercoverage case.
Run an exploratory `mask-coverage` pair with bbox/end_bbox [.18,.20,.40,.50],
baseline and candidate, to distinguish geometry repair from incomplete selection.
This changes selection only and is not a second production fix.

Sparse source inspection also reveals two dataset limitations. In the held-out
bouncy-ball clip the target moves outside the registered static mask (frame 12
approximately x=.69, against the mask right edge .53); this tests a deficient
manual selection, not isolated model replacement quality. The held-out gym crop
contains a burpee-to-standing transition, despite the file title and submitted
prompt referring to jumping jacks. Do not relabel it a clean jumping-jacks test,
change its inputs after inference, or include either case in a model-only success
rate. Report source/action agreement as exploratory with this prompt confound.

The protocol requested sparse real-footage annotations before inference; they
were not completed then. Source labels are now recorded before inspecting held-out
generated frames, but after inference began. Development real-footage labels are
post hoc. This is a protocol deviation, and real motion cannot receive a fully
preregistered quantitative pass. Keep all recordings and results for inspection.
