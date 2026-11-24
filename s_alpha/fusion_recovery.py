"""Read-only recovery inspection; never replay uncertain effects."""
import sqlite3
from contextlib import closing

def pending(db):
    with closing(sqlite3.connect(db)) as c:
        exists=c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='fusion_auth_claims'").fetchone()
        if not exists:
            return []
        return [{"id":i,"digest":d,"state":"uncertain","action":"manual reconciliation required"} for i,d in c.execute("SELECT id,digest FROM fusion_auth_claims WHERE state='running' ORDER BY id")]
