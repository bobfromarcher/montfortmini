import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
import zipfile

import modal_probe
import object_luminance_prompt_candidate as candidate


class LuminancePromptWrapperTests(unittest.TestCase):
    def test_shared_runner_keeps_vace_model_identity_and_bounded_precision_call(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as archive:
            archive.writestr('candidate.json',json.dumps({'failure':None}))
        original=SimpleNamespace(local=Mock(return_value=b'not-used'))
        def nested(inputs,graph):
            modal_probe.masked_replacement.local(graph,{},840,'auto')
            return stream.getvalue()
        with patch.object(modal_probe,'masked_replacement',original), \
             patch.object(candidate.runner.render,'local',side_effect=nested):
            result=candidate.render.local(b'fixture',{'object':'graph'})
        args=original.local.call_args.args
        self.assertEqual(args[1]['mode'],'object-swap')
        self.assertEqual(args[1]['repo'],'Comfy-Org/Wan_2.1_ComfyUI_repackaged')
        self.assertEqual(args[2:],(560,'auto'))
        with zipfile.ZipFile(io.BytesIO(result)) as archive:
            self.assertIn('object-runtime.json',archive.namelist())
