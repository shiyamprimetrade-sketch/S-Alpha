import json
import re
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from s_alpha.fusion_ui import make_server
from s_alpha.fusion_gateway import DEFAULT_PORT

class FusionUITests(unittest.TestCase):
    def test_http_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with make_server(root/"out",root/"db",0) as server:
                thread=threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                try:
                    url="http://127.0.0.1:"+str(server.server_port)
                    with urlopen(url,timeout=5) as r:
                        page=r.read().decode()
                    token=re.search(r'const token="([a-f0-9]{64})"',page).group(1)
                    def call(op,args,auth=token):
                        req=Request(url+"/execute",data=json.dumps(dict(version=3,id=op,operation=op,args=args)).encode(),headers={"Content-Type":"application/json","X-Fusion-Token":auth})
                        with urlopen(req,timeout=5) as r:
                            return json.load(r)
                    with self.assertRaises(HTTPError) as err:
                        call("calculator",{},"bad")
                    self.assertEqual(err.exception.code,403)
                    self.assertEqual(call("calculator",dict(a="2",op="+",b="3"))["data"]["value"],"5")
                    self.assertEqual(call("website",dict(title="T",heading="H",paragraphs=["P"]))["status"],"ok")
                    self.assertTrue((root/"out"/"website"/"index.html").exists())
                    self.assertEqual(call("inventory_register",dict(sku="A",name="Apple",quantity=3))["status"],"ok")
                    self.assertEqual(call("inventory_adjust",dict(sku="A",delta=2))["data"]["quantity"],5)
                    self.assertEqual(call("inventory_search",{})["data"]["products"][0]["quantity"],5)
                    self.assertEqual(call("repair_demo",dict(contract="calculator_add",defect="-"))["data"]["status"],"verified")
                    self.assertEqual(call("fusion_knowledge",{})["data"]["verified"],1)
                finally:
                    server.shutdown()
                    thread.join(5)
    def test_default_port(self):
        self.assertEqual(DEFAULT_PORT,8767)
