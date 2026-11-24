"""Structured local API for integration partners."""
import sqlite3
import subprocess
from .runner import run

def dispatch(task, root, db):
    task_id = task.get("id") if isinstance(task,dict) else None
    def failure(code):
        return {"version":1,"id":task_id if isinstance(task_id,str) else None,"status":"failed","error":{"code":code}}
    if not isinstance(task,dict) or type(task.get("version")) is not int or task["version"] != 1 or task.get("operation") != "build_software" or not isinstance(task_id,str) or not task_id.strip() or not isinstance(task.get("requirement"),str):
        return failure("INVALID_TASK")
    try:
        return run(task,root,db)
    except FileExistsError:
        return failure("ARTIFACT_EXISTS")
    except subprocess.TimeoutExpired:
        return failure("TIMEOUT")
    except ValueError as exc:
        return failure("DUPLICATE_TASK" if str(exc)=="task ID already used" else "UNSUPPORTED_REQUIREMENT")
    except sqlite3.Error:
        return failure("STORAGE_ERROR")
    except OSError:
        return failure("IO_ERROR")
    except RuntimeError:
        return failure("VERIFICATION_FAILED")
