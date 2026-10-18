# Focused review, correction and verification — 2026-10-18

**Release decision: do not promote the experimental correction. The realistic
quality target remains unmet; montfortmini is not ready to be represented as a
convincing Genjutsu-equivalent submission.** Production code is unchanged.

The review found an actual input-information defect: original high-detail
identity inputs were reduced to512px before Qwen's native approximately1MP VAE
conditioning. The old "high-resolution" control enlarged already discarded
pixels with nearest-neighbor; it could not test original-detail retention.
The correction resizes directly from original pixels to an integer multiple of
the legacy canvas, bounded by1MP and available original pixel count. For this
1024x1536 portrait,336x512 becomes672x1024. Models, prompts, seeds and graphs
remain unchanged. The optional research helper is separate from the service.

| Registered comparison | Observed outcome | Frozen reference gate |
|---|---|---|
| Control → original detail in Qwen only | Clear glasses and beard restored, less cartoon-like face. Headwrap persists; target curls absent; hands change. | Fail |
| Detail in both Klein and Qwen | Curls/glasses/beard restored; headwrap removed in final still. Required blazer/ivory shirt lost; head direction and hand placement change. | Fail |

The first test isolates the input policy with matched source pixels, original
identity bytes, graph, prompt, seed42, weights and native Qwen conditioning
dimensions (vision311x474; VAE832x1264). The second is a placement ablation:
Klein latent/token geometry and the intermediate source also change. It does
not isolate a second independent causal mechanism. These are single-seed
observations on a former test clip now used as development, not generalization
or a measured success rate. The apparent bicycle invention was corrected after
inspection: a wheel already exists in the source. Images were assessed by the
coding agent; blinded professional ratings have not been returned.

Success was defined before inference in PROTOCOL.md/candidate-freeze.json.
Neither still met its required identity, clothing and source-posture gate.
Following the declared stopping rule, no new video or unseen-recording inference
was run. There is therefore **no new motion, timing, temporal-stability, anatomy,
raw-video/composited-video or outside-mask preservation pass**. Previous failures
remain. Previously missing source-only timestamp landmarks cannot be invented
retrospectively. The model's failure to preserve identity, clothing and posture
jointly is demonstrated here; source/reference dominance and attention allocation
are possible mechanisms, not established internal causes. Nothing here reveals
Genjutsu's backend.

The independent real object-insertion scale/lighting failure remains unresolved.
Its service/graph/preparation code is byte-identical to the prior release.
Three existing lower-detail references produce pixel-identical prepared images.
Those CPU noninterference checks are not fresh object/motion quality tests.

## Reproduction and evidence

From repository root, with Python dependencies installed:

```sh
python -m unittest discover -s tests -v
python -m unittest test_reference_alignment.py -v
python evaluation/audit_identity_detail.py --control /evidence/old-qwen --candidate /evidence/qwen-original-detail --output paired-audit.json
```

The paired audit is offline and rates no perceptual quality. Exact conditional
GPU entrypoint: `python -m modal run detail_cycle.py --help`. Replays require
authorized compute, an explicitly declared budget.json beside the ledger,
original inputs and the same pinned model artifacts. The video/fresh-source
branches were not exercised because the reference gate failed. Do not assume
the author's credits or evidence paths exist on another checkout.

Public metadata includes freeze/budget, receipts, model revisions/hashes,
workflows, stage environment/logs/resource samples, decisions and input hashes.
Private evidence retains complete original/conditioning images and anchors.
CC0 source copyright metadata is retained, but performer promotional likeness
permission was not established; all human-source derivatives stay out of public
source, demo and social drafts. The original fictional reference is cleared.
The chosen existing models' recorded cards are Apache2.0. No new model or
dependency was added; Ref2VA-VSA remains unrun for documented compatibility and
licensing reasons.

Two GPU attempts completed:360.0531s and407.5169s, total767.5700 worker seconds.
Declared limits:4 attempts/3000s/$2.50 additional included credits. Modal showed
$5.62→$6.17 usage, $24.38→$23.83 remaining, $0 cash/$0 spend cap. The observed
$0.55 delta is not exact per-job billing; asynchronous totals and a conflicting
animated breakdown are retained in the private snapshot. Sampled VRAM values
are in resource-summary.json; allocated RAM is not a measured RAM peak.

## Official checklist and remaining blockers

Rechecked the official app and submission accordions on October18:
https://comfy.org/open-source-higgsfield . Required: Comfy Developer Platform
Router and/or SDK; open-source app/workflows/license/local setup; lawful SFW
cleared media; demo<=2minutes; social demo post with #OpenSourceHiggsfield;
one entry/person and formal submission. Hosted try link is optional. Deadline:
October30,2026 9amPacific/noonEastern. This is judged; no prize is guaranteed.

The real official SDK/self-hosted proxy path, MIT repository, pinned graphs,
setup instructions, existing108-second cleared-media demo and social-post draft
exist. The selected correction failed and is not in that demo or production.
Existing demo remains accurate about the unchanged app and retained failures.
Full independent GPU reproduction, independent professional ratings, registration
confirmation, social publication and formal receipt remain outstanding. Organizer
interpretation of the self-hosted SDK path has not been pre-approved. Required
materials do not substitute for the unmet realistic quality target. No formal
submission, social publication, prize assertion or production deployment occurred.
