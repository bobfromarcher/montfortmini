# Explicit-motion candidate: rejected

One actual GPU video completed October18,2026 at21:54:59 Eastern. It is worse
than the retained protected-reference control. The realistic quality target
and submission-ready decision remain **unmet**. No new held-out run, production
promotion, deployment, social post or formal competition submission followed.

## Observed comparison

Source,full mask and completed-reference float32 tensors match the prior control
exactly. PNG re-encoding changes file hashes,not those pixels. Seed42,480×560,
33frames and8fps are unchanged. The candidate replaces WanAnimate2 raw-video
conditioning with older Wan2.2-Animate14B and explicit body/face controls; it
also changes solver/steps. This is a model/control/solver bundle comparison,
not a one-variable model-capacity experiment.

All33 raw frames were reviewed in11 native-resolution source/control/candidate
contact sheets. The raw/composite PNG arrays are identical under the full mask.
Both fail the unchanged anchored rubric. Agent scores are provisional ordinal
assessments,not independent professional judgments.

| Dimension | Retained control | Explicit-motion candidate |
|---|---|---|
| Reference appearance | Clear glasses/curls/beard in31/33 frames;2 blur-uncertain | No frame clearly establishes the complete fine-attribute requirement; face/eyewear blur and drift |
| Four frozen motion events |2/4 provisional matches |1/4 provisional match;3/4 required |
| Major body continuity | Legs restored in33/33 | Body extends to lower frame,but large blue head extrusion in21..27 |
| Stability/rendering | Previously scored3/4 | Blazer/hand ghosting,white streaks,blur;1/4 |
| Raw/composite | Identical;motion fail | Identical;motion,reference,anatomy and realism fail |

Cross-torso atsource8 fails within6..10. Shoulder/waist at16 has a broad
provisional correspondence at16. Hands-down at24 cannot be established clearly
within22..26 because hands merge into the blazer/waist. Hand-at-mouth at28
fails within26..30;the generated hand remains near the chest. Anatomical failure
alone is sufficient to reject the candidate. No source-identity leak was
demonstrated,so the conditional face-off branch was not authorized by the
frozen protocol. The two unused GPU reservations were not spent.

## What the experiment does and does not establish

The specific approximate body-control pipeline does not solve the observed
motion failure and regresses rendering. It does not establish that this
checkpoint or explicit control generally cannot work. Our MediaPipe33→OpenPose18
map lacks the official whole-body hand detail,retargeting and face-landmark
crop. Source face crops are dark and include some headwear. Upstream rendering
also uses thinner,dimmer elliptical limbs. These are observed preprocessing
differences;their causal contribution is untested.

The pinned safetensors header identifies1441 BF16 tensors. Actual Comfy logs
report `model weight dtype torch.float16`. Stored precision must not be described
as executed BF16 arithmetic. Whether the runtime precision contributes to the
failure is a hypothesis,not an identified cause. Logs show the expected
WAN22_Animate model and no missing-weight warning,OOM or generation exception.
The reference tensor is unchanged. More reference-image rerolls or a larger GPU
are not justified by these results.

Before another quality experiment,the specific technical prerequisite is a
faithful known-good upstream control preparation and checked runtime precision,
followed by a paired comparison against these retained artifacts. That requires
an explicitly frozen new protocol,not recycling this stopped candidate. No
additional payment or hardware requirement has been demonstrated. The separate
realistic object scale/lighting failure remains unresolved.

## Exact execution and resource limits

Model:Comfy-Org/Wan_2.2_ComfyUI_Repackaged,
revisionee6f4a40737a995bf5818954cfce6d59443b0f04,
filewan2.2_animate_14B_bf16.safetensors,34,549,787,368bytes,
SHA2567d37cb0120488dec2a061135aa3018426925318a60838c3de935c829abc88667.
Repository and upstream model/code declare Apache2.0. Existing pinned T5,VAE
and CLIP-VisionH are reused;no relighting or acceleration LoRA.

Comfy commit5cc4b870094c89090db54bd8d12649dcaf89f2ba;official SDK0.5.0,
proxy0.1.6,Torch2.9.1+cu128. Native WanAnimateToVideo,dpmpp_2m/simple,
20steps,CFG1,shift5. Upstream Wan code revision
1ea34ff48f87168174e12956e200b1d908b1c5ff supports base20/CFG1/shift5;
the Comfy solver is not a bit-exact upstream implementation.

Modalcallfc-01M58XS6EBN24FRE1AVW7H1V5C;SDKjobbdeedff1-11f2-4a3a-8618-1cdde5c32d9c.
OneL40S,2CPU,64GiB allocation. Measured worker118.779576558s;Comfy graph96.19s;
CPU controls28.578s. Worker reservation900s of2700s maximum. Actual decode:
33frames,480×560,8fps for source/raw/composite.

GPU/cgroup sample CSV is empty. The executed monitor swallowed errors before
appending the GPU row;the specific exception is unavailable. Peak VRAM,power
and memory usage are **unmeasured**. A post-run correction preserves valid GPU
readings when cgroup data is unavailable and records errors. Its regression
test passes;it has not been GPU-retested. Exact executed modules remain in
executed-source.zip and the original frozen hashes;current source includes only
this telemetry correction relative to that executed runner.

Displayed account usage7.59→7.72;included balance22.41→22.28;cash0 and cash cap0.
The$0.13 rounded,asynchronous UI delta includes CPU builds/preflight/account
activity,not an isolated GPU invoice. No running containers at final check.
The first CPU preflight failed on an omitted transitive module mount;it was
stopped and repaired/refrozen before any GPU dispatch. Both freezes/logs remain.

## Reproduction and release decision

The experiment uses the same CC0 signer recording and original fictional adult
reference listed in the preceding protected-completion study. Human footage,
face crops,landmarks and generated derivatives remain private;copyright
licensing does not establish promotional likeness permission. Public code,
graphs,hashes and factual metadata omit these pixels and controls.

From the repository root:

```sh
PYTHONPATH=. python -m unittest discover -s tests -v
python explicit_motion_controls.py --fixture PRIVATE_CONTROL/inputs --model pose_landmarker_full.task --output NEW_CONTROLS
python evaluation/audit_explicit_motion.py --control PRIVATE_CONTROL --candidate PRIVATE_CANDIDATE --output NEW_REVIEW
python -m modal run explicit_motion_candidate.py --help
```

CPU control preparation needs the separately pinned Python3.11 MediaPipe
environment in evaluation/requirements-reference-isolation.txt. Original input
bytes and hashes,prepared controls,executed graphs,all frames,SDK/Modal receipts,
environments and logs are retained privately. Replay of the stopped inference
requires a new budget and freeze;do not erase the ledger or create a false gate.
The exact executed-source archive predates the telemetry correction. An extracted
Git tree CPU test is setup evidence only,not independent GPU reproduction.

No clean new-machine GPU reproduction,independent professional scoring or
human normal-speed review has occurred. A private blinded review packet is
prepared. Existing cleared108-second demo and submission drafts are unchanged;
they do not demonstrate this failed candidate or realistic parity. Official
rules still require open-source/setup,Comfy SDK/Router integration,a≤2minute
demo,social post and formal entry. Registration,publication and organizer
eligibility interpretation remain unverified. The$10,000 award is judged,not
guaranteed. **Release decision:research evidence retained;candidate rejected.**

Primary sources:
[Comfy rules](https://comfy.org/open-source-higgsfield),
[native guide](https://docs.comfy.org/tutorials/video/wan/wan2-2-animate),
[model card](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged),
[upstream pinned config](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_animate_14B.py).
