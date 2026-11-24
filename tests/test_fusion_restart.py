import tempfile
import unittest
from pathlib import Path
from s_alpha.fusion_keys import load_key
from s_alpha.fusion_authorization import sign,verify_evidence
from s_alpha.fusion_bridge import execute_v3
from s_alpha.fusion_recovery import inspect_claim

class RestartTests(unittest.TestCase):
    def test_restart_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=root/"db"
            path=root/"key"
            key=load_key(path)
            task=dict(version=3,id="calc",operation="calculator",args=dict(a="2",op="+",b="3"))
            evidence=execute_v3(task,sign(task,key),key,root,db,allowed=("calculator",))
            restored=load_key(path)
            self.assertEqual(restored,key)
            self.assertTrue(verify_evidence(evidence,restored))
            self.assertEqual(inspect_claim(db,"calc",restored)["state"],"verified_record")
            with self.assertRaises(ValueError):
                execute_v3(task,sign(task,restored),restored,root,db,allowed=("calculator",))
    def test_corrupt_key_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"key"
            load_key(path)
            path.write_bytes(b"bad")
            with self.assertRaises(ValueError):
                load_key(path)
            self.assertEqual(path.read_bytes(),b"bad")
