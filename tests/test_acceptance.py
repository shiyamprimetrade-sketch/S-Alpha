import unittest
from benchmarks.acceptance import benchmark

class AcceptanceTests(unittest.TestCase):
    def test_benchmark(self):
        result=benchmark()
        self.assertTrue(result["artifact_integrity"])
        self.assertEqual(len(result["cases"]),4)
        self.assertTrue(all(r["baseline_verified"] and r["adaptive_verified"] for r in result["cases"]))
        self.assertFalse(result["promotion_allowed"])
