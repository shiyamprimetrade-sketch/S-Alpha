import hashlib
import sqlite3
import tempfile
import unittest
from contextlib import closing
from html.parser import HTMLParser
from pathlib import Path
from s_alpha.fusion_authorization import authorized_dispatch,sign,verify_evidence
from s_alpha.fusion_recovery import pending

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.data=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
    def handle_data(self,data):
        self.data.append(data)

class IndependentTests(unittest.TestCase):
    def test_artifact_and_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=root/"db"
            key=b"k"*32
            def run(i,op,args):
                t=dict(version=3,id=i,operation=op,args=args)
                e=authorized_dispatch(t,sign(t,key),key,root,db,allowed=(op,))
                self.assertTrue(verify_evidence(e,key))
                self.assertEqual(e["record"]["result"]["status"],"ok")
                return e["record"]["result"]["data"]
            data=run("web","website",dict(title="Title",heading="Heading",paragraphs=["<script>bad</script>"]))
            raw=(root/"web"/"index.html").read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),data["artifact"]["sha256"])
            parser=Parser()
            parser.feed(raw.decode())
            self.assertIn("h1",parser.tags)
            self.assertNotIn("script",parser.tags)
            self.assertIn("<script>bad</script>","".join(parser.data))
            run("reg","inventory_register",dict(sku="A",name="Apple",quantity=10))
            run("adj","inventory_adjust",dict(sku="A",delta=-3))
            with closing(sqlite3.connect(db)) as c:
                self.assertEqual(c.execute("SELECT sku,quantity FROM products").fetchall(),[("A",7)])
    def test_uncertain_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"db"
            with closing(sqlite3.connect(db)) as c,c:
                c.execute("CREATE TABLE fusion_auth_claims (id TEXT PRIMARY KEY,digest TEXT,state TEXT,evidence TEXT)")
                c.execute("INSERT INTO fusion_auth_claims VALUES ('x','digest','running',NULL)")
            self.assertEqual(pending(db)[0]["state"],"uncertain")
            self.assertEqual(pending(db)[0]["id"],"x")
