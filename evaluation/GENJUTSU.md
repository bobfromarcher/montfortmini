# Observable comparator evidence

Observed in the authenticated Genjutsu editor on October 17, 2026: Motion
transfer and Objects swap tabs, reference video duration 4–30 seconds, up to
30 reference images, optional prompt, 720p quality, and an available free
generation switch. The page tool returned model identifier
`hf-mult-motion-control`, seed 42, enhancement false, and effective price 0
when free generation was selected. This identifier is not evidence of the
server's model family, architecture, training data, or internal workflow.

Our prepared comparator uses the development synthetic wave's prepared 480px
source, padded by repeating its final frame to five seconds, and its exact
prepared reference PNG. The original 2.125-second test is below Genjutsu's
minimum duration. The first 17 frames would be compared, with resolution,
duration, padding, encoding and any service crop disclosed. It would not be
a perfectly matched inference configuration.

An earlier 320px upload was rejected by a tool's 340px minimum; an earlier
crop-confirm attempt produced an invalid-duration asset. Neither is a model
quality measurement. The corrected 480px five-second asset was
`3dac7759-4d1b-4e6d-8f6f-83623f7e9ad7`, and its reference asset was
`70cf454d-a52c-4d71-b213-78b4eb15ad97`. The human explicitly approved the
media agreement for these original synthetic fixtures.

The submission request ID `a0197c8a-6a42-4e3d-bc48-4cc43c6eaad1` first
returned `approval_stale` / `before_dispatch`; subsequent receipt/submission
attempts timed out without a confirmed result. No new request ID was used.
The human then reported a free test queued. The remaining visible Genjutsu
history showed a 5-second, 9:16 job using different live-action footage and a
different character reference. That job is not the synthetic benchmark and
is excluded from evaluation. No replacement paid run was submitted.

There is **no verified matched Genjutsu input/output pair** in this evidence
set, and no parity or superiority claim. Screenshots preserve the prepared
free draft and the queued-state mismatch locally; unrelated user media are
not included in the public source repository. Hypotheses that Genjutsu uses
VACE, Animate2, segmentation, tracking, or a particular compositor remain
unsupported. Only our own source and runtime establish our implementation.
