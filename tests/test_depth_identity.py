import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from depth_identity_alignment import depth_policy
from identity_first_alignment import identity_first
import qwen_reference_alignment as qwen
import pose_reference_alignment as pose
import sdk_runner


class DepthIdentityTests(unittest.TestCase):
    def test_third_condition_preserves_identity_order_and_output_geometry(self):
        with identity_first():
            original = qwen.build_graph(prompt=pose.PROMPT)
        with depth_policy(), identity_first():
            graph = qwen.build_graph(prompt=pose.PROMPT)
        for key in ('6', '7'):
            for ref in ('image1', 'image2'):
                self.assertEqual(graph[key]['inputs'][ref], original[key]['inputs'][ref])
            self.assertEqual(graph[key]['inputs']['image3'], ['18', 0])
        for key in ('12', '13'):
            self.assertEqual(graph[key], original[key])

    def test_failed_preparation_restores_graph_prompt_and_sdk_submission(self):
        builder, prompt, sdk = qwen.build_graph, pose.PROMPT, sdk_runner.run_with_sdk
        with self.assertRaises(RuntimeError):
            with depth_policy(), identity_first():
                raise RuntimeError('interrupted')
        self.assertIs(qwen.build_graph, builder)
        self.assertEqual(pose.PROMPT, prompt)
        self.assertIs(sdk_runner.run_with_sdk, sdk)
