"""Read-only recovery inspection; never replay uncertain effects."""
import sqlite3
from contextlib import closing

def pending(db):
    with closing(sqlite3.connect(db)) as c:
        exists=c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='fusion_auth_claims'").fetchone()
        if not exists:
            return []
        return [{"id":i,"digest":d,"state":"uncertain","action":"manual reconciliation required"} for i,d in c.execute("SELECT id,digest FROM fusion_auth_claims WHERE state='running' ORDER BY id")]

def inspect_claim(db,ident,key):
    import json
    from .fusion_authorization import verify_evidence
    with closing(sqlite3.connect(db)) as c:
        row=c.execute("SELECT digest,state,evidence FROM fusion_auth_claims WHERE id=?",(ident,)).fetchone()
    if row is None:
        return {"state":"missing"}
    digest,state,raw=row
    if state=="running":
        return {"state":"uncertain","action":"manual reconciliation required"}
    try:
        evidence=json.loads(raw)
        record=evidence["record"]
        if verify_evidence(evidence,key) and record["id"]==ident and record["request_digest"]==digest and record["result"]["status"]==state:
            return {"state":"verified_record","evidence":evidence}
    except (ValueError,TypeError,KeyError):
        pass
    return {"state":"unverified_record"}
