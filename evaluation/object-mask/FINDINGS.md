# Object-mask localization oracle — October19,2026

**Rejected.** Tighter source-annotated masks reduce the scale proxy but lose
the green reference in all17frames. No object pipeline/model was promoted and
no held-out generation followed. Native motion remains the separate improvement;
the overall realistic two-feature target is still unmet.

The retained bee-recording baseline produced an oversized green ball with
an exploratory generated/source-colored area ratio2.53. Its manual mask spans
12,626pixels, over five times the high-saturation ball component in frame0.
This motivated a spatial-support counterfactual before changing model weights.
The oracle uses framewise source-only yellow-component rectangles plus6px
padding. A first union-mask proposal was retained but never run; its low
saturation threshold included cast shadow. The final high-saturation boxes
were frozen before generation. They are diagnostic annotations, not a production
tracker. Mask size, position and timing change together.

Original source PNGs, reference PNG, settings and complete inference graph are
byte/equality matched to the retained control. VACE1.3B, checkpoint revision,
20steps, seed42, sampler, prompt and reference remain fixed. The mask and its
derived erased-source conditioning change together. The result is **yellow17/17,
green0/17** in both raw and composited frames. Its median yellow-output/source
colored-area ratio is1.2294, but different color/lighting affects that proxy;
it cannot turn the reference-fidelity failure into success.

Raw outside-region MAE/p95 is1.7845/6 on the0–255 scale after8px boundary exclusion;
encoded1.7712/4; composited PNG pixels outside the mask match source exactly.
This separation confirms compositing does not recover the missing appearance.
High-chroma yellow source pixels outside the new mask are zero in14frames and
60/78/90 in the final3. That weakens a simple exposed-ball-pixels explanation;
it does not isolate context, VAE leakage, reference sizing or model capacity.

One L40S call:59.2604worker seconds,43.52Comfy seconds,58GPU samples,
11,906MiB sampled peak. SDK job `a8738797-dfb7-4609-9696-5115003d6cd8`.
Displayed usage8.29→8.33, credits21.71→21.67, cash/cap$0/$0. The account-level
$0.04 delta includes other CPU/account activity; it is not an isolated invoice.
Hard cap was one660-second call and$0.75 included credits; the cycle is closed.

Public source/reference/masks, raw/composited frames, outputs, graph, frozen
source and metrics are retained here with source attribution. The side-by-side
video shows source, old wide-mask green output and the new rejected yellow output.
The old baseline remains at `../quality/samples/new-real-object__candidate__s42`.

```sh
python evaluation/audit_object_mask.py evaluation/object-mask
# Offline preparation only; supply freshly observed billing values:
python evaluation/init_object_mask_replay.py --evidence evaluation/object-mask --output /new/replay-directory --usage YOUR_USAGE --remaining YOUR_CREDITS --confirm-zero-cash-cap
# Optional deliberate paid-credit reproduction; not new held-out evidence:
python -m modal run object_mask_candidate.py --directory /new/replay-directory --confirm-credits-only
```

The offline audit exits1 as expected for the failed green-reference gate,
while reporting artifact invariants separately. It requires OpenCV/NumPy/Pillow;
it contacts no service and performs no generation.

Do not reset a used ledger or reroll this failure. The next discriminating
development test would change only reference spatial registration/conditioning
with the original mask; stronger VACE weights remain a hypothesis, not a proved
requirement. A passing candidate would still need independently selected footage.

Follow-up compatibility correction: historical evaluator capture hooks now call
an explicit local legacy recipe instead of the new cloud orchestrator. Its
regression test verifies no native preparation dispatch. Native inference body
and graphs are unchanged from the successful app check; executed snapshots retain
their original hashes. Local Docker GPU execution and independent review remain
outstanding.
