import json
from pathlib import Path
import tempfile
import unittest
from explicit_motion_workflow import build_graph
from explicit_motion_controls import face_box


class ExplicitMotionTests(unittest.TestCase):
    def test_controls_do_not_use_raw_source_for_body(self):
        graph=build_graph()
        node=graph['7']
        self.assertEqual(node['class_type'],'WanAnimateToVideo')
        self.assertEqual(node['inputs']['pose_video'],['6',3])
        self.assertEqual(node['inputs']['face_video'],['6',4])
        self.assertNotIn('background_video',node['inputs'])
        self.assertNotIn('face_video',build_graph(face=False)['7']['inputs'])
        self.assertEqual(graph['10']['inputs']['trim_amount'],['7',3])

    def test_face_crop_rejects_unobserved_face(self):
        points=[{'x':.5,'y':.1,'visibility':0} for _ in range(33)]
        with self.assertRaises(ValueError):face_box(points,(480,560))

    def test_budget_and_failed_motion_block_followup(self):
        from explicit_motion_candidate import authorize_attempt
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'budget.json').write_text(json.dumps({'cash_cap':0,'stopping_usage':10.59,
                'stopping_remaining':19.41,'max_gpu_attempts':3,'max_worker_seconds':2700}))
            self.assertEqual(authorize_attempt(root,'development',7.62,22.38)[0],[])
            with self.assertRaises(ValueError):authorize_attempt(root,'development',10.59,19.41)
            (root/'gpu-ledger.json').write_text(json.dumps([{'status':'succeeded','kind':'development','ceiling_seconds':900}]))
            (root/'development-review.json').write_text(json.dumps({'motion_pass':False,'identity_leak_demonstrated':False}))
            with self.assertRaises(ValueError):authorize_attempt(root,'face-off',7.9,22.1)
            with self.assertRaises(ValueError):authorize_attempt(root,'verification',7.9,22.1)
            (root/'development-review.json').write_text(json.dumps({'motion_pass':True,'identity_leak_demonstrated':True}))
            self.assertEqual(len(authorize_attempt(root,'face-off',7.9,22.1)[0]),1)

    def test_missing_cgroup_keeps_gpu_sample_and_records_error(self):
        from explicit_motion_candidate import resource_sample
        with tempfile.TemporaryDirectory() as tmp:
            row,error=resource_sample(lambda:'timestamp,99,34000,280',Path(tmp)/'absent')
            self.assertEqual(row,'timestamp,99,34000,280,')
            self.assertEqual(error['stage'],'cgroup-memory')
            self.assertEqual(error['type'],'FileNotFoundError')


if __name__=='__main__':unittest.main()
