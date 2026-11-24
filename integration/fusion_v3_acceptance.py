"""Cross-repository acceptance harness; not production Omega orchestration."""
import hashlib
import hmac
import json
import secrets
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from html.parser import HTMLParser

alpha=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(alpha))
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from omega import canonical,proof
from transactional import seal,verify_record
from journal import Journal
from s_alpha.fusion_bridge import execute_v3

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.text=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
    def handle_data(self,data):
        self.text.append(data)

def require(value):
    if not value:
        raise RuntimeError("acceptance failed")

def main():
    key=secrets.token_bytes(32)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        db=root/"alpha.db"
        journal=Journal(str(root/"omega.db"))
        def signature(task):
            return hmac.new(key,b"alpha-fusion-v3\0"+canonical(task),hashlib.sha256).hexdigest()
        def run(i,op,args,check):
            task=dict(version=3,id=i,operation=op,args=args)
            journal.begin(i)
            e=execute_v3(task,signature(task),key,root,db,allowed=(op,))
            record=e["record"]
            expected=hmac.new(key,b"alpha-fusion-result-v3\0"+canonical(record),hashlib.sha256).hexdigest()
            require(hmac.compare_digest(expected,e["tag"]))
            require(record["id"]==i and record["request_digest"]==proof(task))
            result=record["result"]
            require(result["status"]=="ok" and check(result["data"]))
            omega_record=dict(id=i,status="completed",request_digest=proof(task),result_digest=proof(result))
            sealed=seal(omega_record,key)
            journal.finish(i,"completed",sealed)
            require(verify_record(i,"completed",sealed,key) and journal.get(i)==("completed",sealed))
        def web(data):
            raw=(root/"web"/"index.html").read_bytes()
            page=Page()
            page.feed(raw.decode())
            return hashlib.sha256(raw).hexdigest()==data["artifact"]["sha256"] and "h1" in page.tags and "script" not in page.tags and "<script>x</script>" in "".join(page.text)
        def stock(expected):
            with closing(sqlite3.connect(db)) as c:
                return c.execute("SELECT quantity FROM products WHERE sku='A'").fetchone()==(expected,)
        denied=dict(version=3,id="denied",operation="website",args=dict(title="T",heading="H",paragraphs=["P"]))
        try:
            execute_v3(denied,signature(denied),key,root,db,allowed=())
        except ValueError:
            require(not db.exists() and not (root/"denied").exists())
        else:
            raise RuntimeError("denied task executed")
        run("calc","calculator",dict(a="2",op="+",b="3"),lambda d:d["value"]=="5")
        run("web","website",dict(title="T",heading="H",paragraphs=["<script>x</script>"]),web)
        run("reg","inventory_register",dict(sku="A",name="Apple",quantity=10),lambda d:stock(10))
        run("adj","inventory_adjust",dict(sku="A",delta=-3),lambda d:stock(7))
        run("search","inventory_search",{},lambda d:d["products"][0]["quantity"]==7)
        print(json.dumps({"verified_operations":5,"denied_before_effect":True,"omega_journal":True}))

if __name__=="__main__":
    main()
