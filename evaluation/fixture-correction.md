# Dataset revision 2 correction

Before product tuning, ffprobe showed that the local FFmpeg build ignored the
legacy `-metadata:s:v:0 rotate=90` option. The initial rotation fixture had
transposed stored pixels but no display matrix, so it was legitimately a
portrait video. Its geometry comparison against the intended landscape oracle
was invalid. The initial preflight result is not evidence of a product defect.

The fixture builder now uses `-display_rotation 90` and asserts an actual
side-data rotation of 90 degrees with ffprobe. Dataset revision 1 is preserved
as `dataset-v1-invalid-rotation.json`. Its live-action object generation is kept
under `rejected-input-runs/dev-real-object-v1`, excluded from core case scores.
All raw inputs and its original graph/log/conditioning are retained.

Only the two camera-metadata fixture files changed. Development cube, wave,
walking, and the non-rotated held-out cases retain the same source definitions.
No held-out generated output had been viewed when this correction was made.
Rerun the corrected development baseline before selecting any product repair.
