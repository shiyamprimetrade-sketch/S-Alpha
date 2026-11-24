"""Local, single-user browser interface. No external dependencies."""
import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .pipeline import execute
import hashlib

PAGE = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S-Alpha</title><style>
body{background:#10151d;color:#e6edf3;font:16px system-ui;margin:0 auto;padding:24px;max-width:850px}textarea,pre{box-sizing:border-box;width:100%;background:#192330;color:#e6edf3;border:1px solid #405065;border-radius:8px;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere}button{background:#a7f3d0;color:#10251e;border:0;border-radius:8px;padding:12px;margin:4px;font-weight:bold}label{display:block;margin:12px 0}textarea{min-height:220px}h2{font-size:18px}</style>
<h1>S-Alpha</h1><p>S-Create / S-Learn / S-Universal</p><label for="task">Structured task (JSON)</label><textarea id="task"></textarea><button id="run">Execute task</button><button id="repair">Load repair example</button><button id="knowledge">Knowledge summary</button><h2>Execution evidence</h2><pre id="result" aria-live="polite"></pre><h2>Generated source</h2><pre id="source"></pre>
<script>
const token="__TOKEN__";const task=document.getElementById("task"),result=document.getElementById("result"),source=document.getElementById("source");
function example(repair){let t={version:2,id:"task-"+Date.now(),operation:repair?"repair":"synthesize",spec:{parameters:["a","b"],expression:["add","a","b"]},expected_cases:[[[5,2],7]]};if(repair)t.candidate={parameters:["a","b"],expression:["sub","a","b"]};task.value=JSON.stringify(t,null,2)}
async function send(t){result.textContent="Running...";source.textContent="";try{const r=await fetch("/execute",{method:"POST",headers:{"Content-Type":"application/json","X-Alpha-Token":token},body:JSON.stringify(t)});const data=await r.json();result.textContent=JSON.stringify(data,null,2);source.textContent=data.source||""}catch(e){result.textContent=String(e)}}
document.getElementById("run").onclick=()=>{try{send(JSON.parse(task.value))}catch(e){result.textContent=String(e)}};
document.getElementById("repair").onclick=()=>example(true);
document.getElementById("knowledge").onclick=()=>send({version:2,id:"query",operation:"knowledge"});example(false);
</script></html>"""

def make_server(root,db,port=8766):
    token=secrets.token_hex(32)
    class Handler(BaseHTTPRequestHandler):
        def respond(self,status,body,kind):
            self.send_response(status)
            self.send_header("Content-Type",kind)
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)
        def json_response(self,status,value):
            self.respond(status,json.dumps(value).encode(),"application/json")
        def allowed_host(self):
            return self.headers.get("Host") in ("127.0.0.1:"+str(self.server.server_port),"localhost:"+str(self.server.server_port))
        def do_GET(self):
            if not self.allowed_host() or self.path!="/":
                return self.json_response(404,{"error":"not found"})
            self.respond(200,PAGE.replace("__TOKEN__",token).encode(),"text/html; charset=utf-8")
        def do_POST(self):
            if not self.allowed_host() or self.path!="/execute" or not secrets.compare_digest(self.headers.get("X-Alpha-Token",""),token):
                return self.json_response(403,{"error":"forbidden"})
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0<length<=65536:
                    raise ValueError()
                task=json.loads(self.rfile.read(length))
            except (ValueError,UnicodeError,RecursionError):
                return self.json_response(400,{"error":"invalid request"})
            result=execute(task,root,db)
            if result.get("status")=="verified" and "artifact" in result:
                try:
                    data=(Path(root)/task["id"]/"compute.py").read_bytes()
                    if hashlib.sha256(data).hexdigest()==result["artifact"]["sha256"]:
                        result["source"]=data.decode("utf-8")
                except (OSError,UnicodeError):
                    pass
            self.json_response(200,result)
    return HTTPServer(("127.0.0.1",port),Handler)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=8766)
    p.add_argument("--db",default="alpha.sqlite3")
    p.add_argument("--out",default="workspace")
    a=p.parse_args()
    with make_server(Path(a.out),Path(a.db),a.port) as server:
        print("Open http://127.0.0.1:"+str(server.server_port),flush=True)
        server.serve_forever()

if __name__=="__main__":
    main()
