import tempfile
import unittest
from pathlib import Path
from s_alpha.runner import run
from s_alpha.repair import repair_addition

class RunnerTests(unittest.TestCase):
    def test_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"db"
            task = dict(version=1, operation="build_software", id="x", requirement="calculator")
            run(task, Path(tmp)/"one", db)
            with self.assertRaisesRegex(ValueError,"already used"):
                run(task, Path(tmp)/"two", db)
            self.assertFalse((Path(tmp)/"two").exists())
    def test_repair(self):
        for op in ("-", "*", "+"):
            result = repair_addition("def add(a,b): return a "+op+" b")
            ns = {}
            exec(result["source"], ns)
            for a,b in [(2,3),(-4,1),(0,0),(100,-2)]:
                self.assertEqual(ns["add"](a,b),a+b)
            self.assertEqual(result["changed"],op!="+")
    def test_reject(self):
        with self.assertRaises(ValueError):
            repair_addition("import os")
