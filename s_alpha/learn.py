import sqlite3
import json
from contextlib import closing

def record(db, task_id):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evaluations (task_id TEXT PRIMARY KEY)')
        conn.execute('INSERT INTO evaluations VALUES (?)', (task_id,))

def score(db):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evaluations (task_id TEXT PRIMARY KEY)')
        return conn.execute('SELECT COUNT(*) FROM evaluations').fetchone()[0]

def journal(db, task_id, result):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evidence (seq INTEGER PRIMARY KEY, task_id TEXT, result TEXT)')
        conn.execute('INSERT INTO evidence(task_id,result) VALUES (?,?)', (task_id,json.dumps(result,sort_keys=True)))

def history(db, task_id):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evidence (seq INTEGER PRIMARY KEY, task_id TEXT, result TEXT)')
        return [json.loads(row[0]) for row in conn.execute('SELECT result FROM evidence WHERE task_id=? ORDER BY seq',(task_id,))]

def feedback(db, task_id):
    events = history(db, task_id)
    return {"attempts": sum(e.get("status") in ("failed", "verified") for e in events),
            "retries": sum(e.get("status") == "retry" for e in events),
            "verified": bool(events and events[-1].get("status") == "verified")}
