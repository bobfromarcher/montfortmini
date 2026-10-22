# Release readiness — October22,2026

**Go:** announce the public code preview to technical users with their own
compute. **Pending:** a versioned, verified alpha video release and competition
submission. **Not ready:** a general public generation service or claims of
convincing facial memory/Genjutsu parity.

| Check | Observed result |
|---|---|
| Source distribution | Repository public; main still older; codex/validation contains current native-motion code. No published release/tag at audit time. |
| Current backend availability/auth | Live GET /status returns200 with owner credential and401 without it. No generation job submitted. This tests availability/auth, not a new video. |
| Hosted audience | Existing Sites deployment allows owner only; public access is available as an option but has not been enabled. Frontend's shared backend key would fund visitor jobs if access were widened; no per-visitor compute budget exists. |
| Frontend types | `npx tsc --noEmit` passed on current source, Node24.14.1. |
| Frontend production build | `npm run build` passed on current source; existing dependencies. Not a fresh dependency install or a production browser test. |
| CPU regressions | Last fresh-source suite:61 pass in16.801s, recorded in evaluation/guidance-balance/clean-verification.json. This turn changes documentation only; tests were not repeated. |
| Actual generation | Prior native app-path video and synthetic object proofs retained. No new inference in this release-readiness audit. Exact facial likeness and realistic object quality remain unmet/unproved. |
| Public demo | Existing108-second film is archival. Updated current-native cleared sample and final<=2minute demo pending. Human-source private research footage excluded. |
| Fresh-user GPU setup / review | Independent GPU reproduction and professional review pending. Current local Docker route is provided but not independently executed. |
| Rules | Current expanded official page explicitly permits local ComfyUI; hosted try link optional. Repo/workflows/license/local instructions,<=2minute demo and social demo post remain required. Deadline Oct30,9a.m.Pacific/noonEastern. |
| Formal entry | Registration receipt unverified; no final social URL or submission receipt. |

The code-preview decision does not override any frozen video-quality failure.
Use [RELEASE-PLAN.md](RELEASE-PLAN.md) for the schedule and prospective$5
included-credit planning envelope; it authorizes no GPU dispatch by itself.
Do not infer free generation from MIT source licensing or expose the owner's
shared compute key. Private credentials, source footage and raw smoke-check
captures are excluded from this public report.
