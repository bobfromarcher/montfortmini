# Ref2VA-VSA evaluation

Reviewed October 17, 2026 at upstream commit
`323a0a5f7c636cc70f95464145732f81f04a72e9`.

[Kablex/ComfyUI-Ref2VA-VSA](https://github.com/Kablex/ComfyUI-Ref2VA-VSA)
patches MiniMax H3 reference-to-video attention. Its example graph generates
video and audio from a character image and prompt, using a four-step Turbo
LoRA plus sparse-attention gates. It is not a patch for Wan VACE or Animate2.

The author reports roughly 72 seconds warm / 95 seconds first-run for
1344x768, 124 frames, on an RTX4090, with about 13.5GB peak VRAM. The stated
deployment requirement is a 24GB NVIDIA GPU, native H3 support in ComfyUI,
and a comfy-kitchen CUDA backend exposing `sol_attn`. These claims have not
been independently benchmarked here. The current L40S has sufficient nominal
VRAM, but kernel and node compatibility still require a separate test.

Source review confirms safe-load gate loading, 50-block H3 model checks,
gate-shape validation, and rejection of conflicting attention patches.
The bundled API graph does not establish exact driving-video transfer or
masked object preservation.

## Specific weakness assessed in the validation

Animate2 preserves the development illustration but produces background
ghosting at the end of the live-action walking clip; on the mirrored held-out
arm movement it produces duplicated/ghost arms. These are observed failures,
not evidence that sparse attention fixes them. The VSA patch changes H3's
attention implementation; it does not add a pose/motion signal to our existing
Animate2 graph. Its supplied reference-image generation graph lacks an
equivalent driving-video and mask experiment. Replacing the base model would
confound attention, model family, conditioning and sampling at once.

The appropriate isolated test, if authorized and compatible, would compare
the same H3 weights, seed, prompt, reference, supported driving conditioning,
resolution and frame count with dense attention versus VSA. Score the same
motion phases, reference attributes and ghost/collapse frames, then compare
runtime and VRAM. No such compatible, licensed test is available on this US
deployment, so neither an improvement nor a measured speedup is claimed.

## Licensing and current decision

The node code is Apache-2.0. This does **not** relicense the model weights.
The underlying [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
has territorial restrictions, including the United States, European Union,
United Kingdom and South Korea, plus separate commercial/use conditions.
The [gate weight card](https://huggingface.co/barelymining/ComfyUI-MiniMax-H3-FastVideo)
also identifies that community license. The Turbo adapter's Apache label
does not replace the base-model terms.

The current demonstration runs on a US Modal endpoint. H3 weights were not
downloaded and this plugin was not installed or enabled in the app. Suitable
model authorization must be established before adopting it for that deployment.
Do not install it in this validation. This is a deployment decision based on
the published terms, not a legal opinion.
