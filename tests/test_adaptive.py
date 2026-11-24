import tempfile
import unittest
from pathlib import Path
from s_alpha.knowledge import learn_repair
from s_alpha.adaptive import adaptive_repair, preferences
from s_alpha.debugging import repair

class AdaptiveTests(unittest.TestCase):
    def test_transfer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=root/"db"
            train={"parameters":["a","b"],"expression":["mul","a","b"]}
            bad=dict(train,expression=["add","a","b"])
            learn_repair(db,train,bad,root/"train")
            self.assertEqual(preferences(db),{"add":["mul"]})
            spec={"parameters":["x","y"],"expression":["mul",["sub","x",2],"y"]}
            candidate=dict(spec,expression=["add",["sub","x",2],"y"])
            baseline=repair(spec,candidate,root/"base")
            learned=adaptive_repair(db,spec,candidate,root/"learned")
            self.assertEqual(baseline["status"],"verified")
            self.assertEqual(learned["status"],"verified")
            self.assertEqual(len(baseline["attempts"]),3)
            self.assertEqual(len(learned["attempts"]),2)
    def test_failed_not_learned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            spec={"parameters":["a","b"],"expression":["mul","a","b"]}
            learn_repair(root/"db",spec,dict(spec,expression=["add","a","b"]),root/"out",max_attempts=1)
            self.assertEqual(preferences(root/"db"),{})
    def test_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(preferences(Path(tmp)/"db"),{})
