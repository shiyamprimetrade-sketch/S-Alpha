"""Bounded correction of requirement formatting, never arbitrary source."""
import re
import subprocess
from .universal import build_task
from .learn import journal

def recover(task, root, db):
    requirement = task.get("requirement")
    if not isinstance(requirement, str):
        raise ValueError("requirement must be text")
    normalized = " ".join(re.findall(r"[a-z0-9]+", requirement.casefold()))
    try:
        return build_task(task, root, db)
    except ValueError:
        if normalized == requirement.casefold():
            raise
        journal(db, task["id"], {"status": "retry", "strategy": "normalize punctuation"})
        return build_task(dict(task, requirement=normalized), root, db)
    except subprocess.TimeoutExpired:
        journal(db, task["id"], {"status": "failed", "error": "TimeoutExpired"})
        raise
