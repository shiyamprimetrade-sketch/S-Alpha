from .create import create
from .learn import record

def execute(task, root, db):
    if task.get('version') != 1 or task.get('operation') != 'create_text':
        raise ValueError('unsupported task')
    if not isinstance(task.get('id'), str) or not task['id']:
        raise ValueError('invalid id')
    artifact = create(root, task['name'], task['content'])
    record(db, task['id'])
    return {'version': 1, 'id': task['id'], 'status': 'created', 'artifact': artifact}

from .software import build
from .learn import journal

def interpret(requirement):
    words = requirement.casefold().split()
    matches = [kind for kind in ("calculator", "temperature", "counter", "addition") if kind in words]
    if len(matches) != 1:
        raise ValueError("requirement must identify exactly one supported template")
    return matches[0]

def build_task(task, root, db):
    if task.get("version") != 1 or task.get("operation") != "build_software":
        raise ValueError("unsupported task")
    task_id = task.get("id")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("invalid id")
    try:
        result = build(interpret(task["requirement"]), root)
    except (ValueError, RuntimeError, OSError, TimeoutError) as exc:
        journal(db, task_id, {"status": "failed", "error": type(exc).__name__})
        raise
    result.update(version=1, id=task_id)
    journal(db, task_id, result)
    return result
