# Pinned Wan preprocessing source

Apache License2.0;see LICENSE. Original copyright headers are retained.
Upstream:https://github.com/Wan-Video/Wan2.2 at
1ea34ff48f87168174e12956e200b1d908b1c5ff.

pose2d.py,pose2d_utils.py and human_visualization.py are unchanged upstream
files. face_bbox.py extracts the final get_face_bboxes function unchanged from
upstream utils.py and adds its NumPy import. provenance.json records exact
source hashes and all394 pinned ONNX weight/external-data hashes. Weights are
downloaded from the declared Apache2.0 Wan-AI model repository,not redistributed
here. Other montfortmini source remains under the repository's MIT license.

This experimental integration supports an already cropped single-person input
with the upstream detector=None path. It omits retargeting,YOLO,FLUX and SAM.
It is not advertised as the entire official Wan preprocessing pipeline.
