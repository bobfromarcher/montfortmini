# Public current-motion example â€” October22,2026

The current native backend produces a fictional character following an original
illustrated arm raise. This is cleared synthetic media for a public developer
preview. It is **not a passing exact-face/realistic-quality candidate**.

Watch [source/reference/raw/finished](public-motion-comparison.mp4) at native8fps.
All33 raw frames were retained and provisionally inspected. The character keeps
broad hair/beard/glasses/blue-blazer attributes and follows the arm below shoulder,
outward, then overhead at source0/16/32. Fingers, shoes and facial detail remain
imperfect; the head looks downward. Exact likeness, head turns, occlusion and
cross-shot consistency remain unproved. This known-style synthetic fixture is
not independent held-out footage. Photorealism scores2/4; the full visual gate
therefore remains failed. Raw and composite PNG pixels match in all33 frames
under a full-frame mask, establishing no background-preservation result.

The source is rendered by original MIT `motion_inputs.draw_character` over33
frames (`angle=-0.9+2.2*i/32`) and encoded at8fps. The reference is the retained
original fictional adult character with protected original upper-body pixels
and previously completed fictional lower body. No human performer recording,
Genjutsu output or vendor client asset is included. See [rights](rights.json).
Original uploaded reference and app-prepared reference are both retained.

The graph is unchanged `native_recipe_workflow.build_graph(480,480,33)`:
seed42, six Euler/simple steps,CFG1,shift8, native Wan2.2-Animate converted
checkpoint, Lightx2v and relighting adapters, pinned whole-body/face controls,
Comfy SDK0.5.0/proxy0.1.6. Model hashes are in root `native_recipe_models.py`;
Comfy commit5cc4b870094c89090db54bd8d12649dcaf89f2ba. Exact executed local source
snapshot, workflow, input tensors, runtime source receipts, output frames and
logs are included. Original private evidence.zip remains intact separately.

This run calls the same `native_motion_backend.prepare/render` functions as the
app through a staged replay controller. It checks controls before the sole GPU
call. It is not a new hosted-API/browser generation. All33 control arrays are
finite/nonempty; sampled source/pose/face sheets show a usable arm raise and
cartoon-face crop. The illustration is not a photorealistic face-motion driver.

Measured L40S worker71.745seconds, Comfy graph47.22seconds including loading,
CPU controls78.294seconds. GPU70samples, sampled peak28,981MiB. Host RAM peak
unavailable because the cgroup path was absent. Graph time is not whole-job time.
SDK job7d41fbc7-73d3-4b81-9860-13e3f9daf343; controls call
fc-01M5GX1F7DV0AZ6P5FHE5A1RVJ; GPU callfc-01M5GXBNJ56BS6D55B4S2SHJBF.

The protocol permits only one CPU and one GPU call, each<=900seconds, $1 included
total and $0 cash. Both calls completed; no retries or later tuning. Final
account billing and closeout are retained adjacent to this report. No changes
to production models/settings or deployment followed this example.

The [setup verification](setup-verification.json) uses a genuinely fresh clone,
new Python virtual environment and new npm dependency directory/cache on the
same Windows machine. Installing only root requirements caused a missing-cv2
failure. Installing the existing evaluation requirements resolves it:61tests
pass in41.525seconds, pip check passes, fresh npm installation, types and
production build pass. README now includes the omitted prerequisite.

A fresh local mock sign-in/browser session then uploads these exact public
inputs, submits/polls, switches raw/finished, plays both clips and downloads MP4,
workflow and run details. The UI test uses a loopback adapter replaying this
actual recorded result: **no new inference is performed by that adapter**.
Downloaded MP4 bytes and workflow/manifest JSON match retained artifacts exactly.
The UI and real GPU checks are separate evidence, not one new end-to-end run.
No production credentials were copied into the fresh checkout.

The user confirmed no independent tester is available yet. The setup above is
simulated fresh-user QA by the same agent/operator, not independent approval.
Use [tester instructions](../../submission/TESTER-INSTRUCTIONS.md) and the blank
report to reproduce on another person's account. `init_public_motion_replay.py`
creates a new bounded packet without remote calls; `run_public_motion.py` refuses
used stage ledgers. Replaying these inputs is reproduction, never unseen footage.

Public source/code/media are MIT except bundled upstream components/models,
which retain their original terms/notices. No model weights are redistributed.
The complete current competition demo and independent GPU reproduction remain
outstanding; this4.125-second example can be included with its limitations.

Final live billing: usage8.69→8.75, included credits21.31→21.25, cash charges
and spend cap0. Approximately$0.06 rounded account delta, not an isolated
invoice. Final container list empty. The one-attempt protocol is closed.

Offline check (exit0 means artifact invariants only):

```sh
python evaluation/audit_public_motion.py evaluation/public-motion
```

The fresh-environment audit passes while quality_gate_pass remains false.
The replay initializer was also executed offline into an absent directory;
no cloud calls occur during initialization.
