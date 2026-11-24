import tempfile
import unittest
from pathlib import Path
from s_alpha.api import dispatch

class APITests(unittest.TestCase):
    def test_invalid(self):
        self.assertEqual(dispatch(None,None,None)["error"]["code"],"INVALID_TASK")
    def test_success_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            task=dict(version=1,id="a",operation="build_software",requirement="addition")
            self.assertEqual(dispatch(task,root/"out",root/"db")["status"],"verified")
            self.assertEqual(dispatch(task,root/"out",root/"db")["error"]["code"],"DUPLICATE_TASK")
    def test_unsupported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            task=dict(version=1,id="a",operation="build_software",requirement="chess")
            self.assertEqual(dispatch(task,root/"out",root/"db")["error"]["code"],"UNSUPPORTED_REQUIREMENT")
