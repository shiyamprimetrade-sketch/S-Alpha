import json
import re
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from s_alpha.ui import make_server

class UITests(unittest.TestCase):
    def test_http_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with make_server(p/"out",p/"db",0) as server:
                thread=threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                try:
                    url="http://127.0.0.1:"+str(server.server_port)
                    with urlopen(url,timeout=5) as response:
                        page=response.read().decode()
                    token=re.search(r'const token="([0-9a-f]+)"',page).group(1)
                    task=dict(version=2,id="ui1",operation="synthesize",spec={"parameters":["a"],"expression":["add","a",1]})
                    req=Request(url+"/execute",data=json.dumps(task).encode(),headers={"X-Alpha-Token":token,"Content-Type":"application/json"})
                    with urlopen(req,timeout=5) as response:
                        result=json.load(response)
                    self.assertEqual(result["status"],"verified")
                    self.assertIn("a + 1",result["source"])
                    with self.assertRaises(HTTPError) as ctx:
                        urlopen(Request(url+"/execute",data=b"{}"),timeout=5)
                    self.assertEqual(ctx.exception.code,403)
                finally:
                    server.shutdown()
                    thread.join()
