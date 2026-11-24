import tempfile
import unittest
from pathlib import Path
from s_alpha.fusion_repair import repair_demo,knowledge

class FusionRepairTests(unittest.TestCase):
    def test_calculator(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            r=repair_demo(db,"calculator_add","-")
            self.assertEqual(r["operator"],"+")
            self.assertEqual(r["status"],"verified")
            self.assertEqual(len(r["attempts"]),2)
            self.assertFalse(all(c["passed"] for c in r["attempts"][0]["cases"]))
            self.assertEqual(knowledge(db)["verified"],1)
    def test_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=repair_demo(Path(tmp)/"db","inventory_adjust","*")
            self.assertEqual(r["operator"],"+")
            self.assertEqual(r["attempts"][-1]["cases"][-1]["actual"],"REJECT")
    def test_budget_and_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            for _ in range(2):
                self.assertEqual(repair_demo(db,"calculator_add","-",1)["status"],"failed")
            self.assertEqual(knowledge(db),{"observations":1,"verified":0,"failed":1})
    def test_invalid(self):
        with self.assertRaises(ValueError):
            repair_demo(None,"calculator_add","-",0)
