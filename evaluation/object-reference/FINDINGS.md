# Object conditioning correction cycle — October19,2026

**Both video candidates rejected. Object replacement is not submission-ready.**
No new model, production deployment, or unseen generation follows these failures.
The native motion release is unchanged. This is known bee development footage;
its former held-out status does not carry into these tuned comparisons.

| Contrast versus original wide-mask baseline | Green raw / composite frames | Target/source color-area median | Worker / Comfy graph seconds | Sampled peak GPU |
|---|---|---|---|---|
| Original reference, original instruction prompt |17/17 |2.531 |Historical baseline |Historical baseline |
| Reference subject scaled/translated only |0/17 |No green component |36.038 /19.46 |11,911MiB |
| [Output-description prompt only](../object-prompt/review.json), original reference |17/17 |2.833 |66.574 /45.25 |11,908MiB |

The registered-reference video reconstructs a large yellow target in every
frame. The descriptive-prompt video retains green but has an oversized object
and a persistent hole-like mark on top. Its scale proxy regresses about12%
against the original baseline. Color-area ratios depend on material, lighting
and segmentation; they cannot certify true projected size. Visual inspection
independently rejects the size/shape. Ratings remain provisional agent judgments;
independent normal-speed professional review has not occurred.

Reference registration moves/resamples the existing synthetic sphere on its
original background; source RGB is never pasted into the reference. Crop,
translation, scale and source-only annotation are in mask-annotation.json.
All source PNGs, original wide masks, settings and the complete graph are exact.
Only reference.png and its derived reference tensor change. This does not
separate placement from scale or measure a population effect.

The prompt contrast changes only4.inputs.text. All input archive entries and
conditioning tensors are exact against the original baseline. Its caption
follows the [official VACE guide](https://github.com/ali-vilab/VACE/blob/main/UserGuide.md#31-vace-recognizable-inputs)
recommendation to describe the output. It does not prove that the old word
“yellow” caused the reference failure: this comparison restores the original
large reference and is paired against the original baseline, not the registered
reference run. More scene description and removal of edit instructions change
together. Neither contrast changes model, seed42,20steps,CFG5,uni_pc/simple,
shift8,strength1,480×272,17frames or8fps.

Both frozen protocols retained the earlier acceptance gates: all applicable
visual dimensions>=3/4,15/17 reference frames, no collapse/duplicate target,
area proxy0.8–1.25, centroid error<=0.1 image diagonal, raw/encoded preservation
MAE<=3/255,p95<=10/255 and exact composite pixels outside the binary mask.
Both fail overall. Raw preservation passes: reference contrast1.972/7 MAE/p95;
prompt contrast2.285/7. Encoded preservation passes1.769/4 and1.771/4. Composite
outside-region error is exactly0 for both, attributable to compositing.

The actual model remains VACE1.3B from Comfy-Org/Wan_2.1_ComfyUI_repackaged@
123acf1cc74bccbb9bfff8ac1ee72edc08c2341d; Comfy commit
5cc4b870094c89090db54bd8d12649dcaf89f2ba,SDK0.5.0/proxy0.1.6. Complete graph,
executed source ZIP, input ZIP, revisions, logs, receipts, GPU samples and
failure videos are retained in each case directory. GPU samples35/65 are valid;
host peak RAM is unavailable because the cgroup file was missing. The reference
worker call is fc-01M5B41622AWPRMKYRPPVTEABY, SDK659dabfb-ce6d-478e-9c5e-9b1281764ed7;
prompt fc-01M5B475584TFRH1T0HKV1JSWY, SDK40cd6199-c489-4167-90f9-1c93fb876de2.

Two one-attempt protocols capped each GPU worker at660seconds and$0.75 included
credits, with no retries and a combined$1.50 planning ceiling. They are closed.
Rounded live account usage increased$8.33→$8.41, remaining credits$21.67→$21.59;
cash charges and cash spend limit both$0. The$0.08 account delta includes
associated compute and rounding, not an isolated invoice. No active Modal
containers remained. At least$2 verification credit remains reserved.

Run these offline from the repository root; exit1 is expected because quality
fails while artifact invariants pass:

```powershell
python evaluation/audit_object_reference.py evaluation/object-reference
python evaluation/audit_object_reference.py evaluation/object-prompt --prompt-only
python evaluation/render_object_comparison.py --output review/object-cycle
python -m unittest discover -s tests -p 'test_object_*.py'
```

Set $LiveUsage and $LiveCredits from the current Modal UI. Fresh GPU reproductions require current observed billing, a new directory and
explicit credits-only confirmation. The initializers never dispatch inference;
the Modal entrypoints enforce source/input hashes and reject an existing ledger.
Do not rerun these rejected candidates merely to select a better seed.

```powershell
python evaluation/prepare_object_reference.py --output replay/reference --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_reference_candidate.py --directory replay/reference --confirm-credits-only
python evaluation/prepare_object_prompt.py --output replay/prompt --usage $LiveUsage --remaining $LiveCredits --confirm-zero-cash-cap
python -m modal run object_prompt_candidate.py --directory replay/prompt --confirm-credits-only
```

Next unvalidated technical candidate: object_luminance_inputs.py retains source
luma/geometry within the existing mask while removing RGB chroma. The actual
neutral-erasure path currently removes both appearance and target geometry.
Its code-level two-stream semantics are confirmed in the pinned Comfy
WanVaceToVideo implementation; geometry causing the observed error is still a
hypothesis. Two CPU checks confirm exact outside RGB and achromatic, shaded,
moving inside control. This node has not been mounted in production or run on
GPU. These tests and control images are not improved-video evidence. A future
single-factor paired control test, with fresh billing and budget, is needed
before considering a larger model. No server-side Genjutsu architecture is
established by these experiments.

Media attribution and source hashes: [SOURCE-LICENSE.md](SOURCE-LICENSE.md).
Code remains MIT; attributed bee footage/derivatives are CC BY4.0.

Verification:42 CPU tests pass from a fresh Git source extraction using the existing environment (27.03seconds including offline evidence audits). Both artifact audits and complete case inventories pass; both quality gates fail. This is not a clean dependency install or independent GPU reproduction. A [label-blinded packet](blinded-review.zip) contains the original baseline and both candidates with source/reference/raw/finished media and blank scores; the unblinding key is retained privately. No independent review has been received.
