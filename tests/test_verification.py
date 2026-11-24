import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from s_alpha.verification import verify, build_verified

SPEC={"parameters":["a","b"],"expression":["mul",["add","a","b"],["sub","a","b"]]}

class VerificationTests(unittest.TestCase):
    def test_reference(self):
        result=verify(SPEC,[([5,2],21)])
        self.assertEqual(result["status"],"verified")
        self.assertEqual(result["total"],12)
    def test_wrong_expectation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=build_verified(SPEC,tmp,[([5,2],22)])
            self.assertEqual(result["status"],"failed")
            self.assertFalse((Path(tmp)/"compute.py").exists())
    def test_mutation(self):
        with patch("s_alpha.verification.synthesize",return_value="def compute(a,b): return a+b"):
            self.assertEqual(verify(SPEC)["status"],"failed")
    def test_zero_division(self):
        self.assertEqual(verify({"parameters":["a","b"],"expression":["div","a","b"]})["status"],"verified")
    def test_verified_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=build_verified(SPEC,tmp)
            self.assertEqual(result["status"],"verified")
            self.assertTrue((Path(tmp)/"compute.py").exists())
