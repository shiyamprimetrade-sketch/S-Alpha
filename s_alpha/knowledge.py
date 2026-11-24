"""Persistent, deduplicated observations from controlled repair runs."""
import hashlib
import json
import sqlite3
from contextlib import closing
from .debugging import repair

def encode(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def schema(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS repair_knowledge (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

def learn_repair(db,spec,candidate,root,expected_cases=(),max_attempts=32):
    expected_cases=list(expected_cases)
    result=repair(spec,candidate,root,expected_cases,max_attempts)
    payload={"spec":spec,"candidate":candidate,"expected_cases":expected_cases,"max_attempts":max_attempts,"result":result}
    serialized=encode(payload)
    key=hashlib.sha256(serialized.encode()).hexdigest()
    with closing(sqlite3.connect(db)) as conn,conn:
        schema(conn)
        conn.execute("INSERT OR IGNORE INTO repair_knowledge VALUES (?,?)",(key,serialized))
    return {**result,"knowledge_id":key}

def observations(db):
    with closing(sqlite3.connect(db)) as conn,conn:
        schema(conn)
        return [{"id":key,**json.loads(payload)} for key,payload in conn.execute("SELECT id,payload FROM repair_knowledge ORDER BY rowid")]

def summary(db):
    rows=observations(db)
    return {"observations":len(rows),"verified":sum(r["result"]["status"]=="verified" for r in rows),"failed":sum(r["result"]["status"]=="failed" for r in rows),"candidate_attempts":sum(len(r["result"]["attempts"]) for r in rows)}
