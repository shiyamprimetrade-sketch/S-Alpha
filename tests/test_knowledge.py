import tempfile
import unittest
from pathlib import Path
from s_alpha.knowledge import learn_repair, observations, summary

SPEC={"parameters":["a","b"],"expression":["add","a","b"]}
BAD={"parameters":["a","b"],"expression":["sub","a","b"]}

class KnowledgeTests(unittest.TestCase):
    def test_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=root/"db"
            learn_repair(db,SPEC,BAD,root/"failed",max_attempts=1)
            result=learn_repair(db,SPEC,BAD,root/"success")
            self.assertEqual(result["status"],"verified")
            self.assertEqual(summary(db),{"observations":2,"verified":1,"failed":1,"candidate_attempts":3})
            self.assertEqual(observations(db)[1]["id"],result["knowledge_id"])
    def test_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=learn_repair(root/"db",SPEC,BAD,root/"one")
            second=learn_repair(root/"db",SPEC,BAD,root/"two")
            self.assertEqual(first["knowledge_id"],second["knowledge_id"])
            self.assertEqual(summary(root/"db")["observations"],1)
    def test_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(summary(Path(tmp)/"db")["observations"],0)
