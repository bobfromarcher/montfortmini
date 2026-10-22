# Next candidate: controlled VACE14B comparison (not run)

The measured reference response is weak. Control preparation, prompt-only and
CFG-only changes have not produced a full appearance pass. This supports
testing learned model capacity as a competing explanation, without proving
that capacity is the limiting factor or that a larger model will fix it.

The official [VACE repository](https://github.com/ali-vilab/VACE) lists both
Wan2.1-VACE variants, reference/video/masked editing support, and Apache2.0.
The [official14B model card and license](https://huggingface.co/Wan-AI/Wan2.1-VACE-14B)
also declare Apache2.0. Keep upstream notices; no weights are redistributed.
Existing Comfy GPL obligations and media CC BY terms remain separate from
montfortmini's MIT code license.

The candidate exists at the **same already pinned repackaging revision**:

- Repository: Comfy-Org/Wan_2.1_ComfyUI_repackaged
- Revision: `123acf1cc74bccbb9bfff8ac1ee72edc08c2341d`
- File: `split_files/diffusion_models/wan2.1_vace_14B_fp16.safetensors`
- File size from repository LFS metadata: **34,675,323,640 bytes** (32.29GiB)
- Declared LFS SHA256: `f202a5c59b8a91ada1862c46a038214f1f7f216c61ec8350d25f69b919da4307`

`capacity-model-metadata.json` retains the exact metadata query. No weight file
was downloaded or independently hashed. Do not estimate memory from the14B
name alone: the checkpoint includes additional VACE parameters.

The official [Comfy template](https://github.com/Comfy-Org/workflow_templates/blob/e7cd011d4ded3411c2f481200544f0be6fdc962e/templates/video_wan_vace_14B_t2v.json)
shows native UNETLoader/WanVaceToVideo with the same Wan2.1 VAE and Wan UMT5
loader family. It includes alternate loaders and acceleration LoRAs. Those
LoRAs and template sampler settings are **not** part of the proposed experiment:
adopting them would confound capacity with acceleration/guidance changes.
`capacity-template-evidence.json` records relevant nodes and source hash.
This is compatibility evidence, not a successful load on our pinned runtime.

Next protocol, before any paid work: verify live credits; declare a separate
hard build/download and single-call inference ceiling; reserve verification
credits; validate the pinned14B loader/conditioning shapes. Freeze a graph
using the original green CFG5 repeat, changing the checkpoint only. Keep input
ZIP, text, control, masks, seed42, steps20, shift8, sampler and precision request
fixed. Record unavoidable precision/offloading differences. Same seed does not
make cross-model stochastic trajectories equivalent.

A48GiB L40S may accommodate32.29GiB checkpoint weights with managed offloading
at this small17-frame resolution, but text encoder/VAE/activations/loading copies
make peak VRAM and host RAM uncertain. Budget host RAM explicitly; do not reuse
the old32GiB host allocation blindly. A memory/load failure ends the attempt,
without automatic GPU-tier escalation. No memory or runtime claim is measured
for14B here. The current480x272 diagnostic is below the upstream14B recommended
720p range: retain it for isolation, and disclose that a failure would not rule
out performance at the intended resolution.

Apply the unchanged raw/composite visual gates before considering a winner.
Only a full pass can unlock a reference-selectivity contrast and then genuinely
unseen footage under their own bounds. A failure should identify the measured
failure and close the protocol, rather than begin another preparation sweep.

This is a next-test specification only. The closed CFG protocol authorizes no
additional GPU run, build or model download. No Higgsfield implementation
attribution, guaranteed improvement, eligibility or prize claim follows.
