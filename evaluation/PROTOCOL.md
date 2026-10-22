# montfortmini validation protocol v1

Registered 2026-10-17 before new inference or tuning. Baseline public commit:
`f8373013efb3f83d6135bced808383a8fbdc7100`. A source SHA256 inventory records
the actual local Python files, which are authoritative if they differ.

## Scope and separation

Only object replacement and character motion transfer. Eight short cases:
development and held-out partitions each contain one controlled object case,
one controlled motion case, one live-action object case and one live-action
motion case. Real footage partitions must come from different original files;
temporal crops from one recording do not constitute an independent holdout.
Controlled held-out inputs change geometry/movement and reference appearance.
The previously demonstrated cube and arm wave belong to development only.

Choose source segments, references, prompts, boxes and scoring annotations
before viewing generated outputs. Freeze their hashes in dataset.json. A held-out
case is not used to choose a fix; run it once after the candidate is frozen, with
a paired unchanged baseline for comparison. Any further tuning invalidates its
held-out status and must be disclosed.

## Fixed execution

Use the existing API's 17 frames at 8fps, longest dimension 480, baseline seed 42,
VACE 20 steps / Animate2 10 steps, current pinned models and Comfy commit. No
upscaling or postprocessing beyond current compositing/MP4 export. Repeated
seed 123 is a variance check on development only. Record exact graph, source
and conditioning tensors/frames, masks, reference, package versions, GPU/log,
UTC start/end, SDK job ID, hashes, and wall time. Preserve failures.

At most 24 inference calls and 7,200 cumulative worker seconds. Use one L40S
worker at a time, no volumes, zero warm workers/retries. Check remaining included
credit and a $0 net spend cap before execution. Target <=$6 included credits;
stop if credit/billing evidence no longer supports credits-only execution.

## Acceptance criteria fixed before tuning

These are engineering gates for this small set, not population-level claims.

1. **Technical:** exactly 17 decodable, finite frames of the requested size;
   no missing outputs, truncated files or model exceptions.
2. **Subject/reference fidelity:** >=80% of frames visibly retain the requested
   replacement/character attributes with no disappearance, duplicated subject,
   or major identity/geometry collapse. A reviewer scores reference fidelity
   0 absent/wrong, 1 weak, 2 mixed, 3 clear with minor defects, 4 consistent;
   pass requires >=3. Controlled cases additionally require target-color detection
   in >=80% of frames and intended silhouette/attributes, not color alone.
3. **Motion:** controlled object centroid mean error <=0.10 of frame diagonal
   from the prescribed trajectory; controlled character moving-endpoint mean
   error <=0.12 after torso alignment. For real footage, pre-annotated sparse
   subject/limb points and direction/phase must agree in >=80% of scored frames;
   reviewer motion score >=3/4. Mark untrackable points missing, never zero error.
4. **Temporal stability:** no subject disappearance or catastrophic morphology
   change; reviewer stability >=3/4. Report flow-aligned frame residuals and
   velocity/area jumps as diagnostics, not standalone perceptual proof.
5. **Object background preservation:** before encoding, composite PNG pixels
   outside the exact mask must equal the prepared source exactly. Separately
   score raw output and decoded MP4 outside a dilated mask (8px codec boundary
   exclusion): mean absolute error <=3/255 and 95th percentile <=10/255.
   Label model-generated versus composited preservation explicitly. Motion
   generation changes the full frame, so source-background preservation is
   reported diagnostically and is not an object-preservation claim.

Overall case pass requires every applicable gate, including visual review.
Missing manual scores mean **not independently validated**, not pass. A small
set cannot prove general production readiness or Genjutsu parity.

## Causal experiments and repair rule

On development cases, use identical input, seed, graph and settings except one
factor: object target erasure versus source retained; motion source clip versus
temporally frozen source; reference present versus a neutral reference. Compare
raw and composite outputs without another inference. Use at least one same-seed
repeat to detect nondeterminism and seed 123 to expose seed dependence.

Select one consequential observed failure, state its mechanism as a hypothesis,
make the smallest correction, and rerun the relevant paired development case.
Freeze the candidate before opening held-out outputs. Record both improvements
and regressions; keep the baseline if the evidence does not support the fix.

## Comparator and independent verification

Collect Genjutsu pairs only where its UI clearly offers generation at no extra
cost. Preserve inputs, settings, output and UI evidence. If unavailable, record
the absence; never infer its server model from marketing or similarity.

Produce blinded A/B video order and a separate key, a frame-level annotation
template, quantitative CSV/JSON, and reproduction commands. Agent review is
explicitly labeled; no independent professional review is claimed without one.
Assess Ref2VA-VSA only against an observed failure, checking base-model terms,
node/kernel compatibility and task equivalence before any run.
