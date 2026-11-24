"""Single-use task IDs for the public CLI workflow."""
import sqlite3
from contextlib import closing
from .recovery import recover
from .promotion import active
from .strategy import normalize

def run(task, root, db):
    task_id = task.get("id")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("invalid task id")
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY)")
        try:
            conn.execute("INSERT INTO claims VALUES (?)", (task_id,))
        except sqlite3.IntegrityError as exc:
            raise ValueError("task ID already used") from exc
    if active(db) == 'normalized' and isinstance(task.get('requirement'), str):
        task = dict(task, requirement=normalize(task['requirement']))
    return recover(task, root, db)
