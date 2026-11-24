import tempfile
import unittest
from pathlib import Path
from s_alpha.universal import build_task
from s_alpha.learn import history

class WorkflowTests(unittest.TestCase):
    def test_build_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"evidence.db"
            task = dict(version=1, operation="build_software", id="a", requirement="Build a calculator")
            result = build_task(task, Path(tmp)/"out", db)
            self.assertEqual(result["status"], "verified")
            self.assertEqual(history(db,"a"), [result])
    def test_failure_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"evidence.db"
            task = dict(version=1, operation="build_software", id="b", requirement="Build chess")
            with self.assertRaises(ValueError):
                build_task(task, Path(tmp)/"out", db)
            self.assertEqual(history(db,"b")[0]["status"], "failed")
    def test_ambiguous(self):
        from s_alpha.universal import interpret
        with self.assertRaises(ValueError):
            interpret("calculator temperature")
