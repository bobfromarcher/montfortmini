# Evidence distribution

This repository contains the frozen eight-case submitted input files under
`fixtures/`, the complete 22-row experiment matrix, numerical records, model
hashes, protocol/deviation notes and three original-synthetic sample runs under
`samples/`. Each sample includes source, reference, raw/composite video, graph,
manifest and frame sheets. The sample videos illustrate both success and failure.
Real input clips retain their source CC licenses; see `fixtures/ATTRIBUTION.md`.

The full approximately 300MB validation handoff archive additionally contains
the four complete original recordings, all 22 raw/composite PNG sequences and
conditioning tensors, original execution logs, rejected fixture evidence,
account billing screenshots, an inventory, reproduction source, and the
22-sample offline blind-review packet. It is supplied as a local artifact to
the project owner, rather than committed as large binary data. The findings'
billing and full-run file paths refer to that archive. Independent reviewers
need that archive to recompute all metrics and inspect all frames without
repeating inference. The repository alone supports reviewing selected examples
and replaying the frozen inputs, not independently checking every output claim.
