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
