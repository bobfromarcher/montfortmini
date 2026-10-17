# Genjutsu interface observations — October 17, 2026

Source: the signed-in UI at `https://higgsfield.ai/ai/video?model=genjutsu`,
opened through `https://higgsfield.ai/start/genjutsu`.

These observations concern visible controls only. No generation was submitted,
no media uploaded, and no credits consumed during this inspection. They do not
identify Higgsfield's server-side model, training data, or implementation.

## Motion transfer

- Selected model label: Higgsfield Genjutsu / Reality manipulation.
- Two tabs: Motion transfer and Objects swap.
- Driving video input: visible accepted duration 4–30 seconds.
- Reference images input: visible allowance up to 30 images.
- Apply style settings control is present.
- Prompt is optional behind an initially off toggle.
- Quality selector initially shows 720p; its other values are uninspected.
- A separate Use free gens switch is present and initially off.

## Objects swap

Switching to Objects swap changes the driving video's label from extracting
motion to editing, and removes the Apply style settings button. The 4–30 second
duration and up-to-30 reference inputs remain visible. No mask interface was
observed in the initial empty state; whether it appears after uploading video
is unknown. Do not infer the service uses no masks internally.

## Navigation and examples

The workspace exposes History, Motion Library, How it works, and (in Motion
transfer) Styles. Example cards expose open, expand, and recreate controls.
Batch behavior, queue lifecycle, output export, error handling, and uploaded
input validation are not yet tested.

The prototype uses an original design and independent Comfy workflows. It does
not reproduce Higgsfield branding, copy their assets, or claim feature parity.
