"""Loopback-only Fusion developer preview."""
import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .fusion_gateway import dispatch, DEFAULT_PORT

PAGE="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S Fusion</title><style>
body{background:#10151d;color:#e6edf3;font:16px system-ui;max-width:800px;margin:auto;padding:20px}button,input,textarea,select{font:inherit;padding:12px;border-radius:8px;margin:5px 0;box-sizing:border-box}button{background:#a7f3d0;color:#10251e;border:0;font-weight:bold}input,textarea,select,pre{background:#192330;color:#e6edf3;border:1px solid #405065;width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;box-sizing:border-box}label{display:block;margin-top:12px}button:disabled{opacity:.5}textarea{min-height:90px}</style>
<h1>S Fusion</h1><p>Developer preview · local execution</p>
<label for="operation">Choose operation</label><select id="operation"></select><div id="fields"></div><button id="run">Execute</button><h2>Execution evidence</h2><pre id="result" aria-live="polite"></pre>
<script>
const token="__TOKEN__", select=document.getElementById("operation"), fields=document.getElementById("fields"), result=document.getElementById("result"), run=document.getElementById("run");
const definitions={
calculator:["Calculator",[["a","First number","2"],["op","Operator (+ - * /)","+"],["b","Second number","3"]]],
website:["Generate website",[["title","Page title","Project S"],["heading","Heading","Welcome"],["paragraphs","Content (one paragraph per line)","Built offline.","lines"]]],
inventory_register:["Register product",[["sku","SKU","A1"],["name","Name","Apples"],["quantity","Initial quantity","10","int"]]],
inventory_adjust:["Adjust stock",[["sku","SKU","A1"],["delta","Signed stock change","5","int"]]],
inventory_search:["Search inventory",[["query","Search text",""]]],
repair_demo:["Repair experiment",[["contract","Contract (calculator_add or inventory_adjust)","calculator_add"],["defect","Defective operator","-"],["max_attempts","Attempt limit","4","int"]]],
fusion_knowledge:["Learning evidence",[]]};
for(const [key,value] of Object.entries(definitions)){const option=document.createElement("option");option.value=key;option.textContent=value[0];select.append(option)}
function render(){fields.replaceChildren();for(const [key,label,value,type] of definitions[select.value][1]){const l=document.createElement("label");l.textContent=label;const input=document.createElement(type==="lines"?"textarea":"input");input.id="f-"+key;l.htmlFor=input.id;input.value=value;fields.append(l,input)}}
select.onchange=render;render();
run.onclick=async()=>{run.disabled=true;select.disabled=true;result.textContent="Running...";try{const args={};for(const [key,label,value,type] of definitions[select.value][1]){const v=document.getElementById("f-"+key).value;if(type==="int"&&!/^-?\\d+$/.test(v))throw Error("Invalid integer");args[key]=type==="int"?Number(v):type==="lines"?v.split("\\n"):v}const id=Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,"0")).join("");const r=await fetch("/execute",{method:"POST",headers:{"Content-Type":"application/json","X-Fusion-Token":token},body:JSON.stringify({version:3,id,operation:select.value,args})});result.textContent=JSON.stringify(await r.json(),null,2)}catch(e){result.textContent=String(e)}finally{run.disabled=false;select.disabled=false}};
</script></html>"""

def make_server(root,db,port=DEFAULT_PORT):
    token=secrets.token_hex(32)
    class Handler(BaseHTTPRequestHandler):
        def respond(self,status,data,kind):
            self.send_response(status)
            self.send_header("Content-Type",kind)
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)
        def reply(self,status,value):
            self.respond(status,json.dumps(value).encode(),"application/json")
        def host_ok(self):
            return self.headers.get("Host") in ("127.0.0.1:"+str(self.server.server_port),"localhost:"+str(self.server.server_port))
        def do_GET(self):
            if not self.host_ok() or self.path!="/":
                return self.reply(404,{"error":"not found"})
            self.respond(200,PAGE.replace("__TOKEN__",token).encode(),"text/html; charset=utf-8")
        def do_POST(self):
            supplied=self.headers.get("X-Fusion-Token","")
            if not self.host_ok() or self.path!="/execute" or not supplied.isascii() or not secrets.compare_digest(supplied,token):
                return self.reply(403,{"error":"forbidden"})
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0<length<=65536:
                    raise ValueError()
                self.connection.settimeout(5)
                task=json.loads(self.rfile.read(length))
            except (ValueError,UnicodeError,RecursionError,OSError):
                return self.reply(400,{"error":"invalid request"})
            self.reply(200,dispatch(task,root,db))
    return HTTPServer(("127.0.0.1",port),Handler)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=DEFAULT_PORT)
    p.add_argument("--db",default="fusion.sqlite3")
    p.add_argument("--out",default="fusion-workspace")
    a=p.parse_args()
    with make_server(Path(a.out),Path(a.db),a.port) as server:
        print("Open http://127.0.0.1:"+str(server.server_port),flush=True)
        server.serve_forever()

if __name__=="__main__":
    main()
