import tempfile
import unittest
from pathlib import Path
from s_alpha.fusion_authorization import sign,authorized_dispatch,verify_evidence
from s_alpha.fusion_inventory import Inventory

class AuthorizationTests(unittest.TestCase):
    def test_authorization_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            key=b"k"*32
            task=dict(version=3,id="r1",operation="inventory_register",args=dict(sku="A",name="Apple"))
            for signature,allowed in [("bad",("inventory_register",)),(sign(task,key),())]:
                with self.assertRaises(ValueError):
                    authorized_dispatch(task,signature,key,tmp,db,allowed=allowed)
                self.assertFalse(db.exists())
            evidence=authorized_dispatch(task,sign(task,key),key,tmp,db,allowed=("inventory_register",))
            self.assertTrue(verify_evidence(evidence,key))
            self.assertEqual(len(Inventory(db).search()),1)
            with self.assertRaises(ValueError):
                authorized_dispatch(task,sign(task,key),key,tmp,db,allowed=("inventory_register",))
            evidence["record"]["result"]["status"]="forged"
            self.assertFalse(verify_evidence(evidence,key))
    def test_tampered_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            key=b"k"*32
            task=dict(version=3,id="r",operation="website",args=dict(title="T",heading="H",paragraphs=["P"]))
            signature=sign(task,key)
            task["args"]["title"]="changed"
            with self.assertRaises(ValueError):
                authorized_dispatch(task,signature,key,tmp,db,allowed=("website",))
            self.assertFalse(db.exists())
            self.assertFalse((Path(tmp)/"r").exists())
