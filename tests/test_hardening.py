import tempfile
import unittest
from pathlib import Path
from s_alpha.synthesis import synthesize
from s_alpha.verification import verify
from s_alpha.pipeline import execute

SPEC={"parameters":["a"],"expression":["add","a",1]}
class HardeningTests(unittest.TestCase):
    def test_tree_budget(self):
        expr="a"
        for _ in range(7):
            expr=["add",expr,expr]
        with self.assertRaises(ValueError):
            synthesize(dict(SPEC,expression=expr))
    def test_case_budget(self):
        with self.assertRaises(ValueError):
            verify(SPEC,[([1],2)]*65)
    def test_nonfinite(self):
        with self.assertRaises(ValueError):
            verify(SPEC,[([1],float("nan"))])
    def test_invalid_id(self):
        self.assertIsNone(execute(dict(version=2,id=[]),None,None)["id"])
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/"outside").mkdir()
            try:
                (p/"link").symlink_to(p/"outside",target_is_directory=True)
            except OSError:
                self.skipTest("symlinks unavailable")
            result=execute(dict(version=2,id="link",operation="synthesize",spec=SPEC),p,p/"db")
            self.assertEqual(result["error"]["code"],"UNSAFE_WORKSPACE")
            self.assertFalse((p/"outside"/"compute.py").exists())
