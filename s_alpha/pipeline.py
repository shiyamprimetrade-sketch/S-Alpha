"""Versioned local orchestration of structured arithmetic tasks."""
import sqlite3
from contextlib import closing
from pathlib import Path
from .synthesis import synthesize
from .verification import build_verified
from .knowledge import learn_repair, summary
from .learn import journal

def execute(task,root,db):
    task_id=task.get("id") if isinstance(task,dict) else None
    def failure(code):
        return {"version":2,"id":task_id,"status":"failed","error":{"code":code}}
    if not isinstance(task,dict) or type(task.get("version")) is not int or task["version"]!=2 or not isinstance(task_id,str) or not task_id or len(task_id)>64 or not task_id.isascii() or not all(c.isalnum() or c in "_-" for c in task_id):
        return failure("INVALID_TASK")
    op=task.get("operation")
    if op not in ("synthesize","repair","knowledge"):
        return failure("INVALID_OPERATION")
    try:
        if op=="knowledge":
            return {"version":2,"id":task_id,"status":"ok","knowledge":summary(db)}
        spec=task["spec"]
        synthesize(spec)
        expected=task.get("expected_cases",[])
        if op=="repair":
            synthesize(task["candidate"])
        with closing(sqlite3.connect(db)) as conn,conn:
            conn.execute("CREATE TABLE IF NOT EXISTS pipeline_claims (id TEXT PRIMARY KEY)")
            try:
                conn.execute("INSERT INTO pipeline_claims VALUES (?)",(task_id,))
            except sqlite3.IntegrityError:
                return failure("DUPLICATE_TASK")
        out=Path(root)/task_id
        if op=="repair":
            result=learn_repair(db,spec,task["candidate"],out,expected,task.get("max_attempts",32))
        else:
            result=build_verified(spec,out,expected)
        result.update(version=2,id=task_id)
        journal(db,task_id,result)
        return result
    except (ValueError,KeyError,TypeError,OverflowError):
        return failure("INVALID_SPEC")
    except sqlite3.Error:
        return failure("STORAGE_ERROR")
    except OSError:
        return failure("IO_ERROR")
