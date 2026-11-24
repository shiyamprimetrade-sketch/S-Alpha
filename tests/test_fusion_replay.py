import tempfile
import unittest
from pathlib import Path
from s_alpha.fusion_gateway import dispatch
from s_alpha.fusion_inventory import Inventory

class ReplayTests(unittest.TestCase):
    def test_replay_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            Inventory(db).register("A","Apple",10)
            task=dict(version=3,id="adjust1",operation="inventory_adjust",args=dict(sku="A",delta=5))
            first=dispatch(task,tmp,db)
            self.assertEqual(first["data"]["quantity"],15)
            self.assertEqual(dispatch(task,tmp,db),first)
            self.assertEqual(Inventory(db).search()[0]["quantity"],15)
            task["args"]["delta"]=7
            self.assertEqual(dispatch(task,tmp,db)["status"],"failed")
            self.assertEqual(Inventory(db).search()[0]["quantity"],15)
    def test_failed_adjustment_does_not_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            inv=Inventory(db)
            inv.register("A","Apple",1)
            with self.assertRaises(ValueError):
                inv.adjust("A",-2,"retry")
            self.assertEqual(inv.adjust("A",2,"retry"),3)
