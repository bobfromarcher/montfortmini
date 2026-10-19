# Genjutsu: deeper client trace, October 19

**Result:** the inspected client submission contract is substantially clearer.
Genjutsu's server inference code, checkpoint identity, weights and training have
not been recovered. This investigation establishes no improvement in our videos.

## What the delivered source establishes

Followed explicit imports from the retained editor into its final serializers,
job submitters, shared HTTP transport and optional video crop exporter. REA
parsed 11 additional client modules and three media-preparation modules without
parse failures. Semantic coverage remains unknown: the first scope alone has
2,281 unresolved semantic observations. Raw vendor code and full REA evidence
remain private and are not included under this repository's license.

| Stage | Observed behavior | Consequence |
| --- | --- | --- |
| Builder helper | The previously unresolved helper adds community-preset attribution. | It is not a concealed local reference-image generation step. |
| Final motion serializer | Media roles and asset IDs/types, prompt, resolution, aspect ratio, optional dimensions, scene mode and selected character ID. | No generated first frame, skeleton, mask or checkpoint is sent in this inspected serializer. Server derivation remains possible. |
| Final object serializer | Resolution, attribution, batch size, optional dimensions, media IDs/types, optional prompt/folder. | The earlier absence-of-mask observation now extends through the final serializer on this path. It does not prove absence of server segmentation. |
| Submission | JSON POST to `/jobs/v2/hf_mult_motion_control` or `/jobs/v2/hf_mult_replace_object`, under the observed production gateway; separate free-generation flags. | These routing labels do not identify a diffusion model. A flag is not proof of free billing. No job was submitted. |
| Optional browser preparation | Skip unchanged local files; otherwise crop frames through a canvas into AVC MP4, trim when requested, and attempt audio preservation. | This is ordinary media preparation, not observed neural conditioning. Its use for our historical job is unknown. |
| Source maps | No `sourceMappingURL` directive in the 139 retained JavaScript files scanned. | No linked original-source map was available from those directives; this is not proof that no other map exists. |

Locations, file digests, source URLs and explicit limitations are recorded in
[the facts ledger](genjutsu-client/DEEPER-OBSERVATIONS.json). That ledger contains
derived observations, not captured proprietary source.

## Corroboration and a correction to the earlier report

The official [motion-transfer API reference](https://open.higgsfield.ai/models/higgsfield/genjutsu/motion-transfer/v1.0/api-reference)
is now readable without the previously observed login redirect. It documents
video/image URLs, optional prompt, three output resolutions, a four-second source
minimum, trimming beyond 30 seconds, and 1–8 image references. The
[object-swap reference](https://open.higgsfield.ai/models/higgsfield/genjutsu/object-swap/v1.0/api-reference)
also specifies at least 409,600 source pixels per frame. These are API-version
contracts; the inspected web client permits up to 30 references. Do not collapse
those interfaces or marketing limits into one specification.

Comfy's public `nodes_higgsfield.py`, Git blob
`4d0a2cfc84e0799dc41be3c8791b0a1917e95216`, independently uploads inputs to a
partner API, polls request status, and downloads a result. It does not contain
Genjutsu inference code. Its seed widget only forces re-execution; seed is not
included in the submitted model request. A matching UI seed therefore cannot
make a matched deterministic Genjutsu experiment. The fetched file's Git blob
identity was independently recomputed and matched the directory inventory.

Authenticated History still shows the retained completed motion-transfer job
as 720p, five seconds. It exposes the Genjutsu product label, not a backbone or
checkpoint. Other video elements coexist on the page, so their dimensions and
durations are not attributed to that job without a DOM association.

## What follows for montfortmini

Our reference-editing and Wan/VACE choices are independent design choices;
this evidence does not establish that Higgsfield uses them. In particular,
browser media ordering does not determine neural image-conditioning order.
Neither API wrappers nor recovered UI code can substitute for passing raw-video
quality gates.

One concrete independent correction is justified by our own workflow audit:
the previously tested base-only approximation omitted the official native
template's converted checkpoint, acceleration adapter and relighting adapter,
and used a different sampler configuration. A separately budgeted, frozen
native-recipe diagnostic tests that bundle, starting with a source-character
oracle. It retains the smaller diagnostic dimensions and frame rate; it must not
be described as bit-exact reproduction of the complete official template or
as Higgsfield's implementation. Its [experiment report](native-recipe/FINDINGS.md)
records a provisional development improvement and a technical failure during
unseen-output packaging; generalization remains unverified.

Research itself used zero GPU jobs, zero generation jobs and $0 cash. The app's
quality verdict remains **not demonstrated** until a candidate passes the
unchanged reference, motion, anatomy and temporal gates and independent footage.
