"""Controlled operator repair; no execution of arbitrary source."""
import hashlib
import json
import sqlite3
from contextlib import closing
from .fusion_contracts import CONTRACTS,evaluate
from .fusion_calculator import calculate

def repair_demo(db,contract,defect,max_attempts=4):
    if contract not in CONTRACTS or defect not in ("+","-","*","/") or type(max_attempts) is not int or not 1<=max_attempts<=4:
        raise ValueError("invalid repair request")
    attempts=[]
    for op in dict.fromkeys((defect,"+","-","*","/")):
        if len(attempts)>=max_attempts:
            break
        def candidate(a,b):
            if contract=="calculator_add":
                return calculate(a,op,b)
            value=calculate(a,op,b)
            from decimal import Decimal
            n=Decimal(value)
            if n!=n.to_integral_value() or not 0<=n<=1000000000:
                raise ValueError("stock out of bounds")
            return str(int(n))
        rows=evaluate(contract,candidate)
        attempts.append({"operator":op,"cases":rows})
        if all(r["passed"] for r in rows):
            break
    verified=all(r["passed"] for r in attempts[-1]["cases"])
    result={"contract":contract,"defect":defect,"status":"verified" if verified else "failed","operator":attempts[-1]["operator"] if verified else None,"attempts":attempts}
    payload=json.dumps(result,sort_keys=True,separators=(",",":"))
    key=hashlib.sha256(payload.encode()).hexdigest()
    with closing(sqlite3.connect(db)) as c,c:
        c.execute("CREATE TABLE IF NOT EXISTS fusion_repair_evidence (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        c.execute("INSERT OR IGNORE INTO fusion_repair_evidence VALUES (?,?)",(key,payload))
    return dict(result,knowledge_id=key)

def knowledge(db):
    with closing(sqlite3.connect(db)) as c,c:
        c.execute("CREATE TABLE IF NOT EXISTS fusion_repair_evidence (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        rows=[json.loads(r[0]) for r in c.execute("SELECT payload FROM fusion_repair_evidence")]
    return {"observations":len(rows),"verified":sum(r["status"]=="verified" for r in rows),"failed":sum(r["status"]=="failed" for r in rows)}
