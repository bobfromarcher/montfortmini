import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import service
import native_motion_backend
import modal_probe


def request(mode):
    return {'mode':mode,'video_b64':'YQ==','reference_b64':'Yg=='}


class NativeRoutingTests(unittest.TestCase):
    def test_nested_native_wrapper_forwards_the_precision_argument(self):
        from unittest.mock import Mock
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as archive:
            archive.writestr('candidate.json','{}')
        original=SimpleNamespace(local=Mock(return_value=b'not-used'))
        def nested(inputs,graph):
            modal_probe.masked_replacement.local(graph,{},840,'auto')
            return stream.getvalue()
        with patch.object(modal_probe,'masked_replacement',original), \
             patch.object(native_motion_backend.candidate.render,'local',side_effect=nested):
            native_motion_backend.render.local(b'fixture',{'native':'graph'})
        args=original.local.call_args.args
        self.assertEqual(args[2:],(840,'auto'))
        self.assertEqual(args[1]['mode'],'motion-transfer')
        self.assertIn('User-selected',args[1]['input_provenance'])

    def test_failed_native_bundle_is_returned_to_the_private_evidence_caller(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as archive:
            archive.writestr('candidate.json',json.dumps({'status':'failed','failure':{'type':'TestFailure'}}))
        prep=SimpleNamespace(object_id='fc-prepare-test',get=lambda:{'inputs':b'fixture','graph':{}})
        render=SimpleNamespace(object_id='fc-render-test',get=lambda:stream.getvalue())
        with patch.object(service.native_motion_backend.prepare,'spawn',return_value=prep), \
             patch.object(service.native_motion_backend.render,'spawn',return_value=render):
            result=service.generate.local(request('motion-transfer'),retain_evidence=True)
        self.assertEqual(result['technical_failure'],{'type':'TestFailure'})
        with zipfile.ZipFile(io.BytesIO(result['evidence_zip'])) as archive:
            self.assertIn('candidate.json',archive.namelist())
            self.assertIn('service-job.json',archive.namelist())

    def test_motion_uses_one_controls_call_and_one_native_render(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream,'w') as archive:
            for name in ('source.mp4','generated.mp4','composite.mp4'):
                archive.writestr(name,b'test-video-bytes')
            archive.writestr('candidate.json',json.dumps({'status':'succeeded'}))
            archive.writestr('manifest.json',json.dumps({'sdk_job_id':'unit-test'}))
            archive.writestr('workflow-api.json',json.dumps({'native':'graph'}))
        prep = SimpleNamespace(object_id='fc-prepare-test',get=lambda:{'inputs':b'fixture','graph':{'native':'graph'}})
        render = SimpleNamespace(object_id='fc-render-test',get=lambda:stream.getvalue())
        with patch.object(service.native_motion_backend.prepare,'spawn',return_value=prep) as prepare_call, \
             patch.object(service.native_motion_backend.render,'spawn',return_value=render) as render_call, \
             patch.object(service.generate_object,'remote') as object_call:
            result = service.generate.local(request('motion-transfer'),retain_evidence=True)
        self.assertEqual(prepare_call.call_count,1)
        render_call.assert_called_once_with(b'fixture',{'native':'graph'})
        object_call.assert_not_called()
        with zipfile.ZipFile(io.BytesIO(result['evidence_zip'])) as archive:
            calls=json.loads(archive.read('service-job.json'))
            self.assertEqual(calls['render_call_id'],'fc-render-test')
        self.assertEqual(result['workflow'],{'native':'graph'})

    def test_object_stays_on_existing_object_worker(self):
        with patch.object(service.generate_object,'remote',return_value={'test':'object'}) as object_call, \
             patch.object(service.native_motion_backend.prepare,'spawn') as prepare_call:
            self.assertEqual(service.generate.local(request('object-swap')),{'test':'object'})
        self.assertEqual(object_call.call_count,1)
        prepare_call.assert_not_called()
