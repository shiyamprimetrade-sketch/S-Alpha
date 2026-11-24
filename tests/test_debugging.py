import tempfile
import unittest
from pathlib import Path
from s_alpha.debugging import repair

SPEC={"parameters":["a","b"],"expression":["add","a","b"]}
BAD={"parameters":["a","b"],"expression":["sub","a","b"]}

class DebuggingTests(unittest.TestCase):
    def test_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=repair(SPEC,BAD,tmp,[([5,2],7)])
            self.assertEqual(result["status"],"verified")
            self.assertEqual(result["attempts"][0]["status"],"failed")
            self.assertIn("a + b",(Path(tmp)/"compute.py").read_text())
    def test_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=repair(SPEC,BAD,tmp,max_attempts=1)
            self.assertEqual(result["status"],"failed")
            self.assertFalse((Path(tmp)/"compute.py").exists())
    def test_conflicting_expectation(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(repair(SPEC,BAD,tmp,[([5,2],99)])["status"],"failed")
    def test_correct_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(repair(SPEC,SPEC,tmp)["attempts"]),1)
