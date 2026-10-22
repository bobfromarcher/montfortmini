import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
import numpy as np
from reference_branch_inputs import receipt_arrays,OpenJutsuConditioningReceipt


class BranchReceiptTests(unittest.TestCase):
    def inputs(self):
        frames=np.arange(1*32*6*2*3,dtype=np.float32).reshape(1,32,6,2,3)
        mask=np.zeros((1,64,6,2,3),np.float32)
        meta=dict(vace_frames=[frames],vace_mask=[mask])
        return [[np.ones((1,4,8),np.float32),meta]],[[np.zeros((1,3,8),np.float32),meta]],dict(samples=np.zeros((1,16,6,2,3),np.float32))

    def test_receipt_splits_reference_from_control_without_mutation(self):
        pos,neg,latent=self.inputs();before=pos[0][1]['vace_frames'][0].copy()
        arrays=receipt_arrays(pos,neg,latent,1)
        self.assertEqual(arrays['reference_prefix'].shape,(1,32,1,2,3))
        self.assertEqual(arrays['control_tail'].shape,(1,32,5,2,3))
        np.testing.assert_array_equal(np.concatenate((arrays['reference_prefix'],arrays['control_tail']),axis=2),before)
        np.testing.assert_array_equal(pos[0][1]['vace_frames'][0],before)
        self.assertFalse(np.array_equal(arrays['positive_text'],arrays['negative_text']))

    def test_rejects_unexpected_packing_and_negative_conditioning_mismatch(self):
        pos,neg,latent=self.inputs()
        with self.assertRaises(ValueError):receipt_arrays(pos,neg,latent,0)
        neg[0][1]=dict(vace_frames=[np.zeros_like(pos[0][1]['vace_frames'][0])],vace_mask=pos[0][1]['vace_mask'])
        with self.assertRaisesRegex(ValueError,'Negative VACE'):receipt_arrays(pos,neg,latent,1)

    def test_receipt_node_returns_original_objects_and_writes_loadable_snapshots(self):
        pos,neg,latent=self.inputs()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch('reference_branch_inputs.Path',return_value=root):
                result=OpenJutsuConditioningReceipt().record(pos,neg,latent,1,42)
            self.assertIs(result[0],pos);self.assertIs(result[1],neg);self.assertIs(result[2],latent)
            with np.load(root/'wan-conditioning.npz') as z:
                self.assertEqual(set(z.files),{'positive_text','negative_text','reference_prefix','control_tail','vace_mask','initial_latent'})
