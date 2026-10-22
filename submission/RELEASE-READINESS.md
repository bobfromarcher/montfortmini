# Release readiness â€” October22,2026

**Go:** announce the public code preview to technical users with their own
compute. **Pending:** independent user/account reproduction, a published alpha and competition
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
| Public demo | Current cleared4.125-second native-motion source/reference/raw/finished example completed; see evaluation/public-motion. Exact face/realism gate remains unmet. Final<=2minute competition film pending;108-second older film archival. |
| Fresh-user setup / review | Fresh clone, isolated Python/npm dependencies,61CPU tests, types/build and fixture-backed simulated browser user pass. Missing OpenCV evaluation install instruction corrected. Independent person/account/GPU reproduction remains pending. |
| Rules | Current expanded official page explicitly permits local ComfyUI; hosted try link optional. Repo/workflows/license/local instructions,<=2minute demo and social demo post remain required. Deadline Oct30,9a.m.Pacific/noonEastern. |
| Formal entry | Registration receipt unverified; no final social URL or submission receipt. |

The code-preview decision does not override any frozen video-quality failure.
Use [RELEASE-PLAN.md](RELEASE-PLAN.md) for the schedule and prospective$5
included-credit planning envelope; it authorizes no GPU dispatch by itself.
Do not infer free generation from MIT source licensing or expose the owner's
shared compute key. Private credentials, source footage and raw smoke-check
captures are excluded from this public report.
