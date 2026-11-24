import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from s_alpha.doctor import diagnose

class MobileTests(unittest.TestCase):
    def test_doctor(self):
        self.assertTrue(diagnose()["ready"])
    def test_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            task=p/"task.json"
            task.write_text(json.dumps(dict(version=2,id="mobile",operation="synthesize",spec={"parameters":["a"],"expression":["add","a",1]})),encoding="utf-8")
            cmd=[sys.executable,"-m","s_alpha","--db",str(p/"db"),"execute",str(task),"--out",str(p/"out")]
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"],"verified")
            self.assertNotEqual(subprocess.run(cmd,capture_output=True,timeout=15).returncode,0)
