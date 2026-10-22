import unittest
from modal_probe import missing_output_error
from service import render_failure_message


class RenderFailureTests(unittest.TestCase):
    def test_retains_execution_cause_instead_of_only_missing_frame_count(self):
        error=missing_output_error(17,0,"[ERROR] !!! Exception during processing !!! No module named 'cv2'\nTraceback: internal details\n")
        self.assertIn("No module named 'cv2'",str(error))
        self.assertIn('Expected 17 frames, received 0',str(error))
        self.assertNotIn('internal details',str(error))

    def test_uses_last_bounded_error_and_has_missing_log_fallback(self):
        text='Exception during processing !!! old\nException during processing !!! '+('x'*1000)
        self.assertLess(len(str(missing_output_error(17,0,text))),320)
        self.assertNotIn('old',str(missing_output_error(17,0,text)))
        self.assertEqual(str(missing_output_error(17,0,'')),'Expected 17 frames, received 0.')

    def test_api_identifies_dependency_failure_without_exposing_traceback(self):
        message=render_failure_message(RuntimeError("Expected17 frames, received0. Comfy error: No module named 'cv2'; private traceback"))
        self.assertIn('server configuration error',message)
        self.assertNotIn('private traceback',message)
        self.assertNotIn('Try a shorter clip',message)
