import tempfile
import unittest
from pathlib import Path
from s_alpha.fusion_gateway import dispatch,DEFAULT_PORT

class GatewayTests(unittest.TestCase):
    def test_demo_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"out"
            db=Path(tmp)/"db"
            def run(op,args):
                return dispatch(dict(version=3,id="demo",operation=op,args=args),root,db)
            self.assertEqual(run("calculator",dict(a="2",op="+",b="3"))["data"]["value"],"5")
            self.assertEqual(run("inventory_register",dict(sku="A",name="Apple",quantity=2))["status"],"ok")
            self.assertEqual(run("inventory_adjust",dict(sku="A",delta=3))["data"]["quantity"],5)
            self.assertEqual(run("inventory_search",{})["data"]["products"][0]["quantity"],5)
            self.assertEqual(run("repair_demo",dict(contract="calculator_add",defect="-"))["data"]["status"],"verified")
            self.assertEqual(run("fusion_knowledge",{})["data"]["verified"],1)
    def test_legacy_and_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            self.assertEqual(dispatch(dict(version=2,id="query",operation="knowledge"),tmp,db)["version"],2)
            self.assertEqual(dispatch(dict(version=3,id="../bad",operation="website"),tmp,db)["error"]["code"],"INVALID_TASK")
            self.assertEqual(dispatch(dict(version=3,id="x",operation="unknown"),tmp,db)["error"]["code"],"INVALID_OPERATION")
            self.assertEqual(DEFAULT_PORT,8767)
