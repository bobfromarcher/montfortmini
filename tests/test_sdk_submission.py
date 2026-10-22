import json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sdk_runner import run_with_sdk


class SubmissionReceipt(unittest.TestCase):
    def test_poll_failure_keeps_receipt_and_never_resubmits(self):
        job=Mock(id='known-job');job.wait.side_effect=TimeoutError('polling timed out')
        client=Mock();client.submit.return_value=job
        factory=Mock();factory.return_value.__enter__=Mock(return_value=client)
        factory.return_value.__exit__=Mock(return_value=False)
        with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,{'comfy_sdk':types.SimpleNamespace(Comfy=factory)}),patch.dict('os.environ',{},clear=True),patch('builtins.print') as log:
            with self.assertRaises(TimeoutError):run_with_sdk({'1':{}},temp,timeout=80)
            self.assertEqual(json.loads((Path(temp)/'job-receipt.json').read_text())['job_id'],'known-job')
            log.assert_called_once_with('Comfy SDK confirmed job: known-job',flush=True)
        self.assertEqual(client.submit.call_count,1)
        factory.assert_called_once_with(timeout=80)
        job.wait.assert_called_once_with(timeout=80)


if __name__=='__main__':unittest.main()
