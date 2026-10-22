# Independent tester packet — current native motion example

No independent tester has run this packet yet. The maintainer's clean Windows
clone/install is recorded separately and does not establish another user's
GPU reproduction. Please report failures as well as successes.

## 1. Use a fresh checkout and your own environment

Clone the exact commit recorded by this release, rather than mixing files from
different branches. The public candidate branch is `codex/validation` until a
versioned alpha is published. Install Python3.12+ and Node22.13+; the recorded
clean CPU setup used Python3.14.4/Node24.14.1 on Windows. FFmpeg/ffprobe must be
available for local video evaluation. GPU execution below uses your own Modal
account; model/pose downloads happen remotely.

```sh
git clone --depth 1 --branch codex/validation https://github.com/bobfromarcher/montfortmini.git
cd montfortmini
git rev-parse HEAD
python -m venv .venv
```

Activate `.venv` (`.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` on Linux/macOS), then:

```sh
python -m pip install -r requirements.txt -r evaluation/requirements.txt
python -m pip check
python -m unittest discover -s tests
cd webapp
npm run install:ci
npx tsc --noEmit
npm run build
cd ..
```

The evaluation requirements are necessary: the minimal root requirements alone
leave OpenCV missing for the test suite. This omission in the earlier README
was found and corrected during the clean-install check.

Record OS, CPU/RAM, Python/Node versions, source commit, installation commands,
exit codes and any deviations in the blank report. Keep credentials out of logs.
Passing these CPU/frontend checks is not a GPU or video-quality pass.

## 2. Optional independently funded GPU replay

Use your own included credits or other compute you have authorized. Check live
billing and set your account's cash cap to$0 if using only credits. The packet
requires at least$3 remaining and reserves at most$1 included for one CPU
preparation and one L40S GPU attempt (each<=900seconds). New accounts or uncached
images may need more build/download credit than the maintainer's cached run;
if the$1 total cannot cover setup, stop and report that resource blocker.
Do not buy credits, raise a cap, add persistent storage or retry automatically.

Run `python -m modal setup` yourself. Do not use the maintainer's key, deploy
their Sites project or send them your token. The replay makes no public endpoint.
Replace the illustrative8.00/22.00 numbers with your live usage/balance:

```sh
python evaluation/init_public_motion_replay.py --example evaluation/public-motion --output results/my-public-motion-replay --usage 8.00 --remaining 22.00 --confirm-zero-cash-cap
python evaluation/run_public_motion.py controls results/my-public-motion-replay --confirm-credits-only
```

Unzip the resulting `inputs.zip` into a new local folder. Watch its source/pose
frames and inspect the face crops. Check a single continuous body and the
source's raising arm. Do not assume the skeleton is correct because preparation
completed. If it fails, stop before GPU and report it.

Only after passing that review, create `controls-review.json` in the replay
directory with `gate_pass: true`, your notes, and `inputs_sha256` equal to the
actual SHA256 of its `inputs.zip`. For example:

```json
{"gate_pass": true, "inputs_sha256": "REPLACE_WITH_ACTUAL_SHA256", "review": "REPLACE_WITH_YOUR_OBSERVATIONS"}
```

Then execute once:

```sh
python evaluation/run_public_motion.py render results/my-public-motion-replay --confirm-credits-only
```

The stage ledgers reject reuse. Never delete a used ledger to retry. A failed
run requires a new explained protocol, not a hidden rerun. Save final billing
totals and confirm your account has no unwanted running containers.

## 3. Evaluate the output and return evidence

Use the recorded public source/reference and every raw frame, then inspect the
composite separately at native480x480/8fps. The original example is33frames,
4.125seconds, seed42, six steps. Compare the arm below shoulder, rising outward,
then above shoulder (source0/16/32). Report timing deviations and skipped motion.
Inspect facial proportions/glasses and hands independently of clothing/color.
If view/resolution cannot establish likeness, mark it unassessable. Stable
clothing alone cannot pass exact facial consistency. This synthetic illustration
does not test realistic head turns, occlusion or consistency across shots.

Return a completed `TESTER-REPORT-TEMPLATE.json`, commands/logs without secrets,
source/model/workflow hashes, raw and finished clips, failure timecodes, GPU
allocation, timings and measured account-credit delta. Include the original
reference, not just the app-prepared one. Bit-identical cross-machine output is
not required; compare behavior and disclose runtime differences.

Public inputs here are original synthetic media; rights/provenance and retained
failure notes accompany the example. Share additional clips only when you have
permission to publish their content/likeness. No report is counted as an
independent pass until the tester actually returns evidence. This packet has
not been sent to anyone by the maintainer's assistant.
