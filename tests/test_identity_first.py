import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identity_first_alignment import identity_first, relabel
import pose_reference_alignment as previous
import qwen_reference_alignment as qwen


class IdentityFirstTests(unittest.TestCase):
    def test_pair_only_changes_reference_slots_and_labels(self):
        original = qwen.build_graph(prompt=previous.PROMPT)
        expected = copy.deepcopy(original)
        for key in ('6', '7'):
            inputs = expected[key]['inputs']
            inputs['image1'], inputs['image2'] = inputs['image2'], inputs['image1']
        expected['6']['inputs']['prompt'] = relabel(previous.PROMPT)
        with identity_first():
            actual = qwen.build_graph(prompt=previous.PROMPT)
        self.assertEqual(actual, expected)
        self.assertEqual(actual['12'], original['12'])
        self.assertEqual(relabel(relabel(previous.PROMPT)), previous.PROMPT)

    def test_interrupted_trial_cannot_leak_policy_into_frozen_helpers(self):
        builder, prompt = qwen.build_graph, previous.PROMPT
        with self.assertRaises(RuntimeError):
            with identity_first():
                raise RuntimeError('interrupted')
        self.assertIs(qwen.build_graph, builder)
        self.assertEqual(previous.PROMPT, prompt)
