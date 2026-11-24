import tempfile
import unittest
import sqlite3
from contextlib import closing
from pathlib import Path
from s_alpha.fusion_inventory import Inventory

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"inventory.db"
        self.inv=Inventory(self.db)
    def test_persistence_and_stock(self):
        self.inv.register("A1","Apples",10)
        self.assertEqual(self.inv.adjust("A1",5),15)
        self.assertEqual(self.inv.adjust("A1",-3),12)
        self.assertEqual(Inventory(self.db).search("apple"),[dict(sku="A1",name="Apples",quantity=12)])
        with closing(sqlite3.connect(self.db)) as c:
            self.assertEqual(c.execute("SELECT quantity FROM products WHERE sku='A1'").fetchone(),(12,))
    def test_rejected_updates_preserve_stock(self):
        self.inv.register("A1","Apples",2)
        for delta in (-3,1000000000,True,1.5):
            with self.assertRaises(ValueError):
                self.inv.adjust("A1",delta)
        self.assertEqual(self.inv.search()[0]["quantity"],2)
    def test_registration(self):
        self.inv.register("A1","Apples")
        for sku,name,q in [("A1","Duplicate",0),("../x","Bad",0),("B","",0),("B","Bad",-1),("B","Bad",True)]:
            with self.assertRaises(ValueError):
                self.inv.register(sku,name,q)
        self.assertEqual(len(self.inv.search()),1)
    def test_search_literal_and_limit(self):
        self.inv.register("B","100% stock")
        self.inv.register("A","Other")
        self.assertEqual(self.inv.search("%")[0]["sku"],"B")
        self.assertEqual(self.inv.search("' OR 1=1 --"),[])
        self.assertEqual(self.inv.search(limit=1)[0]["sku"],"A")
    def test_unknown(self):
        with self.assertRaises(ValueError):
            self.inv.adjust("missing",1)
