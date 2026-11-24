import tempfile
import unittest
from pathlib import Path
from s_alpha.promotion import active, promote
from s_alpha.runner import run
from s_alpha.learn import history

class PromotionTests(unittest.TestCase):
    def test_persist_and_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"db"
            self.assertEqual(active(db),"raw")
            result = promote(db,[("calculator!","calculator")],[("counter?","counter")])
            self.assertTrue(result["promoted"])
            self.assertEqual(active(db),"normalized")
            task = dict(version=1,operation="build_software",id="p",requirement="addition!")
            self.assertEqual(run(task,Path(tmp)/"out",db)["status"],"verified")
            self.assertEqual([x["status"] for x in history(db,"p")],["verified"])
    def test_reject_tie(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"db"
            self.assertFalse(promote(db,[("calculator!","calculator")],[("counter","counter")])["promoted"])
            self.assertEqual(active(db),"raw")
    def test_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                promote(Path(tmp)/"db",[("calculator","calculator")],[("Calculator","calculator")])
    def test_reject_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"db"
            promote(db,[("calculator!","calculator")],[("counter?","counter")])
            result = promote(db,[("calculator","calculator")],[("addition!","addition")])
            self.assertFalse(result["promoted"])
            self.assertEqual(active(db),"normalized")
