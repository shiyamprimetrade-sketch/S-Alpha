import tempfile
import unittest
from pathlib import Path
from s_alpha.pipeline import execute
from s_alpha.learn import history

SPEC={"parameters":["a","b"],"expression":["add","a","b"]}
class PipelineTests(unittest.TestCase):
    def test_synthesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            task=dict(version=2,id="one",operation="synthesize",spec=SPEC)
            self.assertEqual(execute(task,p/"out",p/"db")["status"],"verified")
            self.assertTrue((p/"out"/"one"/"compute.py").exists())
            self.assertEqual(history(p/"db","one")[0]["status"],"verified")
            self.assertEqual(execute(task,p/"out",p/"db")["error"]["code"],"DUPLICATE_TASK")
    def test_repair_knowledge(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            task=dict(version=2,id="repair1",operation="repair",spec=SPEC,candidate=dict(SPEC,expression=["sub","a","b"]))
            self.assertEqual(execute(task,p/"out",p/"db")["status"],"verified")
            result=execute(dict(version=2,id="query",operation="knowledge"),p/"out",p/"db")
            self.assertEqual(result["knowledge"]["verified"],1)
    def test_invalid(self):
        self.assertEqual(execute(dict(version=2,id="../escape",operation="synthesize"),None,None)["error"]["code"],"INVALID_TASK")
    def test_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            task=dict(version=2,id="bad",operation="synthesize",spec=SPEC,expected_cases=[([2,3],99)])
            self.assertEqual(execute(task,p/"out",p/"db")["status"],"failed")
            self.assertFalse((p/"out"/"bad"/"compute.py").exists())
