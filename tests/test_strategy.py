import tempfile
import unittest
from pathlib import Path
from s_alpha.software import build
from s_alpha.strategy import train, predict
from benchmarks.strategy_benchmark import benchmark

class StrategyTests(unittest.TestCase):
    def test_repaired_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(build("addition",tmp)["status"],"verified")
            self.assertIn("return a + b",(Path(tmp)/"addition.py").read_text())
    def test_held_out(self):
        result = benchmark()
        self.assertEqual(result,{"selected":"normalized","raw":3,"selected_score":6,"total":6})
    def test_empty(self):
        with self.assertRaises(ValueError):
            train([])
    def test_ambiguous(self):
        self.assertIsNone(predict("calculator, counter!","normalized"))
