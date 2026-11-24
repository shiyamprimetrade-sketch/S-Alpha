import tempfile
import unittest
from pathlib import Path
from s_alpha.recovery import recover
from s_alpha.learn import history

class RecoveryTests(unittest.TestCase):
    def test_punctuation_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"evidence.db"
            task = dict(version=1, operation="build_software", id="r", requirement="Build calculator!")
            self.assertEqual(recover(task, Path(tmp)/"out", db)["status"], "verified")
            self.assertEqual([x["status"] for x in history(db,"r")], ["failed","retry","verified"])
    def test_unsupported(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"evidence.db"
            task = dict(version=1, operation="build_software", id="r", requirement="chess")
            with self.assertRaises(ValueError):
                recover(task, Path(tmp)/"out", db)
            self.assertEqual(len(history(db,"r")), 1)

    def test_counter_feedback(self):
        from s_alpha.learn import feedback
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"evidence.db"
            task = dict(version=1, operation="build_software", id="c", requirement="Build counter!")
            self.assertEqual(recover(task, Path(tmp)/"out", db)["kind"], "counter")
            self.assertEqual(feedback(db,"c"), {"attempts":2,"retries":1,"verified":True})
