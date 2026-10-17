# Phase 2 experiment decisions

Five completed development profiles inspected: sheet, crop, describe, separate,
native. Whole-sheet conditioning retains multiple panels. Selecting one portrait
improves a single face, but imposes a headshot and gray letterbox bands. Separate
source caption and higher resolution do not recover hands or source framing.
Native size improves apparent fine detail but leaves border artifacts. No winner
selected and no new realistic quality claim made.

The two VAE files have identical full tensor payload hashes and all tensor
headers (194 tensors); only container metadata differs. This rules out the
proposed VAE mismatch for these bytes. No VAE substitution is justified.

Next planned contrasts before their inference:
1. native -> cover: same image/caption/resolution/seed; replace padded reference
   with center-cover fitting, consistent with the native node's documented crop.
2. cover -> fullbody: one frontal full-body panel from the same reference sheet;
   no other graph or sampler change. Tests framing/limb visibility, not model IP.
3. If useful, test the chosen preparation with production graph/default prompt,
   since descriptive per-case driving captions are not an existing user input.

Private original media and all derivatives remain outside the public repository.
Genjutsu settings, seed and backend are unknown; do not claim causal superiority.

The production-default portrait contrast confirms removal of the gray bands at
the existing 272x480/8fps, with no graph/prompt changes. The proposed production
patch is frozen as a candidate, not yet deployed. Its center crop can cut full
bodies in wide output frames, so recheck the already-viewed walking failure
before prospective held-out inference. If that regression is material, reject
the global default rather than tune against the new held-outs.

New source-only review rejected a nearly static 52s push-up interval before any
generated test output existed. The revised 71..73.125s interval contains a clear
high-plank to lowered-body phase. The original rejected source selection and
its first freeze are retained. This is source curation, not model-output tuning.

Full-body development run logged a Modal runner idle/restart warning before one
successful function result. Reserve one additional infrastructure attempt against
the 16-attempt cap; worker metadata does not measure that failed runner's cost.

First prospective synthetic-object attempt failed after confirmed SDK submission,
inside GET job status polling (`httpx.ReadTimeout`, 30s HTTP read timeout), after
65.12s client time. No generated output was returned or inspected. Original
failure log and ledger row retained. Comfy/proxy subprocesses were terminated
by the existing finally block; this was not an unconfirmed-submit resubmission.

Necessary execution repair: use `client.submit` once, immediately save the
confirmed job receipt, then wait on that job; bound individual HTTP reads at
min(120s, job timeout). No submission retry is introduced. Evaluator now archives
inputs/graph/log/receipt on future failure. Sampling graph, weights and seed are
unchanged. Freeze the repair before an explicit rerun. Drop the synthetic-motion
baseline run to preserve the phase's total ceiling: 15 recorded attempts plus
one reserved Modal runner failure, at most 16. This protocol deviation limits
paired inference evidence for the new synthetic motion case.

Final selection after the prospective pair: reject global center-cover fitting.
The push-up candidate crops the reference's feet and later changes the framing;
both profiles retain an upright figure rather than the source's horizontal body.
The portrait and walking background improvements do not establish a universally
better default. Restore exact phase-1 rotation-corrected media preparation
(`1b205eea...aaa3`) and retain the candidate as a frozen experimental module.
Ship only the supported SDK polling/receipt repair. No sampling/model change.

The original API graph builder is unchanged; model revisions are unchanged.
Two object cases and the aspect-matched synthetic motion case have identical
reference pixels under the two preparations; quantify this as input identity,
not an unexecuted baseline inference. The real-motion baseline was actually run
with the repaired SDK and is direct evidence for the retained default.

The private prepared portrait reference is delivered separately for inspection
or reuse. Its better appearance is a limited headshot result and is not a pass
for the source's missing hand motion or source setting.
