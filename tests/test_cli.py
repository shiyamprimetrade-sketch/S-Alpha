import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

class CLITests(unittest.TestCase):
    def test_train_build_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root/"data.json"
            dataset.write_text(json.dumps({"training":[["calculator!","calculator"]],"validation":[["counter?","counter"]]}))
            def cli(*args):
                result = subprocess.run([sys.executable,"-m","s_alpha","--db",str(root/"db"),*args],capture_output=True,text=True,check=True,timeout=20)
                return json.loads(result.stdout)
            self.assertTrue(cli("train",str(dataset))["promoted"])
            state = cli("strategy")
            self.assertEqual(state["active"],"normalized")
            self.assertEqual(len(state["audit"][0]["dataset_sha256"]),64)
            self.assertEqual(cli("build","addition!","--id","demo","--out",str(root/"out"))["status"],"verified")
            self.assertTrue(cli("history","demo")["feedback"]["verified"])
