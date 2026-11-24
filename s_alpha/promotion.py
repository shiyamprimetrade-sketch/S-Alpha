"""Persist a strategy only when it strictly improves a separate validation set."""
import sqlite3
import json
import hashlib
from contextlib import closing
from .strategy import train, evaluate

def active(db):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS strategy_state (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        row = conn.execute("SELECT name FROM strategy_state WHERE id=1").fetchone()
        return row[0] if row else "raw"

def promote(db, training, validation):
    training, validation = list(training), list(validation)
    if not training or not validation:
        raise ValueError("nonempty training and validation required")
    if {x[0].strip().casefold() for x in training} & {x[0].strip().casefold() for x in validation}:
        raise ValueError("training/validation overlap")
    candidate = train(training)
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("BEGIN IMMEDIATE")
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS strategy_state (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
            row = conn.execute("SELECT name FROM strategy_state WHERE id=1").fetchone()
            current = row[0] if row else "raw"
            before, after = evaluate(validation,current), evaluate(validation,candidate)
            accepted = after > before
            if accepted:
                conn.execute("INSERT OR REPLACE INTO strategy_state VALUES (1,?)",(candidate,))
            result = {"candidate":candidate,"active":candidate if accepted else current,"promoted":accepted,"before":before,"after":after,"total":len(validation)}
            result["dataset_sha256"] = hashlib.sha256(json.dumps([training,validation],ensure_ascii=False).encode("utf-8")).hexdigest()
            conn.execute("CREATE TABLE IF NOT EXISTS promotion_audit (seq INTEGER PRIMARY KEY, result TEXT NOT NULL)")
            conn.execute("INSERT INTO promotion_audit(result) VALUES (?)",(json.dumps(result),))
            return result

def audit(db):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS promotion_audit (seq INTEGER PRIMARY KEY, result TEXT NOT NULL)")
        return [json.loads(row[0]) for row in conn.execute("SELECT result FROM promotion_audit ORDER BY seq")]
