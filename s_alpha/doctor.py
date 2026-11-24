"""Portable environment and local capability checks."""
import json
import platform
import sqlite3
import sys
import tempfile
from pathlib import Path
from .pipeline import execute
from .ui import make_server

def diagnose():
    checks={"python":sys.version_info >= (3,11)}
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)
        try:
            result=execute({"version":2,"id":"doctor","operation":"synthesize","spec":{"parameters":["a"],"expression":["add","a",1]}},p/"out",p/"db")
            checks["pipeline"]=result["status"]=="verified"
            checks["artifact"]=(p/"out"/"doctor"/"compute.py").is_file()
        except (OSError,sqlite3.Error):
            checks["pipeline"]=False
        try:
            with make_server(p/"out",p/"db",0):
                checks["loopback"]=True
        except OSError:
            checks["loopback"]=False
    return {"platform":platform.system(),"machine":platform.machine(),"python_version":platform.python_version(),"checks":checks,"ready":all(checks.values())}

if __name__=="__main__":
    result=diagnose()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["ready"] else 1)
