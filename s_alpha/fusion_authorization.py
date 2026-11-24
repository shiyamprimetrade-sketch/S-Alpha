"""Candidate v3 authenticated local adapter, separate from legacy v2."""
import hashlib
import hmac
import json
import re
import sqlite3
from contextlib import closing
from .fusion_gateway import dispatch

OPERATIONS=frozenset(("calculator","website","inventory_register","inventory_adjust","inventory_search","repair_demo","fusion_knowledge"))

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")

def sign(task,key):
    if not isinstance(key,bytes) or len(key)<32:
        raise ValueError("invalid key")
    raw=canonical(task)
    if len(raw)>65536:
        raise ValueError("request too large")
    return hmac.new(key,b"alpha-fusion-v3\0"+raw,hashlib.sha256).hexdigest()

def authorized_dispatch(task,signature,key,root,db,*,allowed=()):
    expected=sign(task,key)
    if not isinstance(signature,str) or not signature.isascii() or not hmac.compare_digest(expected,signature):
        raise ValueError("authentication failed")
    # Snapshot authenticated content before dispatch.
    raw=canonical(task)
    snapshot=json.loads(raw)
    if not hmac.compare_digest(sign(snapshot,key),signature):
        raise ValueError("request changed")
    if not isinstance(snapshot,dict) or set(snapshot)!={"version","id","operation","args"} or type(snapshot["version"]) is not int or snapshot["version"]!=3:
        raise ValueError("invalid envelope")
    ident,op=snapshot["id"],snapshot["operation"]
    if not isinstance(ident,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",ident) or not isinstance(op,str) or op not in OPERATIONS or op not in allowed or not isinstance(snapshot["args"],dict):
        raise ValueError("operation denied or invalid envelope")
    digest=hashlib.sha256(raw).hexdigest()
    with closing(sqlite3.connect(db)) as c,c:
        c.execute("CREATE TABLE IF NOT EXISTS fusion_auth_claims (id TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL, evidence TEXT)")
        try:
            c.execute("INSERT INTO fusion_auth_claims VALUES (?,?,'running',NULL)",(ident,digest))
        except sqlite3.IntegrityError as exc:
            raise ValueError("replayed task") from exc
    result=dispatch(snapshot,root,db)
    record={"id":ident,"request_digest":digest,"result":result}
    evidence={"record":record,"tag":hmac.new(key,b"alpha-fusion-result-v3\0"+canonical(record),hashlib.sha256).hexdigest()}
    with closing(sqlite3.connect(db)) as c,c:
        c.execute("UPDATE fusion_auth_claims SET state=?,evidence=? WHERE id=?",(result["status"],canonical(evidence).decode("ascii"),ident))
    return evidence

def verify_evidence(evidence,key):
    try:
        if not isinstance(key,bytes) or len(key)<32:
            return False
        tag=evidence["tag"]
        return isinstance(tag,str) and tag.isascii() and hmac.compare_digest(tag,hmac.new(key,b"alpha-fusion-result-v3\0"+canonical(evidence["record"]),hashlib.sha256).hexdigest())
    except (KeyError,TypeError,ValueError):
        return False
