import tempfile
import unittest
from pathlib import Path
from s_alpha.synthesis import synthesize, build_expression

class SynthesisTests(unittest.TestCase):
    def test_composition(self):
        spec={"parameters":["a","b"],"expression":["mul",["add","a","b"],["sub","a","b"]]}
        ns={}
        exec(synthesize(spec),ns)
        for a,b in [(5,2),(-3,4),(0,0),(100,1)]:
            self.assertEqual(ns["compute"](a,b),(a+b)*(a-b))
    def test_constants(self):
        ns={}
        exec(synthesize({"parameters":["c"],"expression":["add",["div",["mul","c",9],5],32]}),ns)
        self.assertEqual(ns["compute"](100),212)
    def test_reject_injection(self):
        with self.assertRaises(ValueError):
            synthesize({"parameters":["a"],"expression":"__import__('os')"})
    def test_invalid_parameter(self):
        with self.assertRaises(ValueError):
            synthesize({"parameters":["class"],"expression":1})
    def test_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=build_expression({"parameters":["a"],"expression":["add","a",1]},tmp)
            self.assertEqual(result["status"],"generated")
            self.assertTrue((Path(tmp)/"compute.py").exists())
