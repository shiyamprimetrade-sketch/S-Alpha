import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess
from s_alpha.software import build

class SoftwareTests(unittest.TestCase):
    def test_calculator(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(build("calculator", tmp)["status"], "verified")
            self.assertTrue((Path(tmp)/"calculator.py").is_file())
    def test_temperature(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(build("temperature", tmp)["status"], "verified")
    def test_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build("shell", tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])
    def test_failed_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("s_alpha.software.subprocess.run", return_value=CompletedProcess([], 1, "", "failure")):
                with self.assertRaises(RuntimeError):
                    build("calculator", tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])
