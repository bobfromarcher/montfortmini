# Confirmation of frozen cascade-v1

Source recording/crop/reference selection was frozen before candidate output. Pipeline code hashes are frozen in candidate-freeze.json before this recording is generated. No model, prompt, mask, crop or sampler tuning is permitted from these outputs. Retain the first result, successful or not.

Two final GPU attempts are reserved: one fresh real recording (33frames) and one known synthetic-motion regression (17frames). Run sequentially. Existing phase budget is eight GPU attempts total, 3600 worker seconds, and $2.50 included credits from the $3.38 snapshot; $0 cash cap remains. Each full-cascade call has a900sec ceiling; reserve the full ceiling before starting and do not start another call if remaining measured/reserved time is insufficient. If a new infrastructure failure occurs, inspect it before any retry. These are attempts7 and8, not more development tuning.

Rubric inherited from RUBRIC.md and earlier anchored protocol: applicable dimensions>=3/4, no persistent limb collapse or duplicate/missing source-visible hands; reference glasses/hair/wardrobe recognizable in at least ceil(14/17*N) frames. For N33 the threshold is28; for N17 it is14. Track reference face geometry separately from colors/clothing. Source-visible gesture timing must have at least3/4 defined landmarks in order within2frames at8fps; the real source includes right-hand rise across chest and toward face while the other hand remains near waist. Signing semantic correctness is not claimed or assessed. Source has a headwrap and low light; target has visible salt-and-pepper curls and clear round glasses. Both are expected attribute challenges, recorded before rendering.

Raw and composited video outputs must be evaluated separately; a full-frame motion mask makes their PNG pixels identical, which is checked rather than treated as a compositing-quality gain. Background is generated; no exact source-background pixel-preservation claim. This one new recording is not a population-level quality estimate, and the old synthetic clip is not held out.

The published object-replacement engine and masks were not changed in this phase. Its prior independent real-object scale/lighting failure remains disclosed, while existing synthetic success and zero outside-mask PNG compositing evidence remain retained. No new object-model quality claim follows from this motion-only correction.

Final-attempt budget clarification, before submission: see final-regression-budget.json and EDITOR-PROTOCOL.md. The final regression has a tighter660sec ceiling, with the same frozen inference. No further GPU attempts follow it.

Publication note: relative document links above were normalized for this repository layout. Inference code/frozen hashes were not changed.
