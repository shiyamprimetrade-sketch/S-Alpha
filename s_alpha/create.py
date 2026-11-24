from pathlib import Path
import hashlib

def create(root, name, content):
    if not name or Path(name).name != name or name in ('.', '..') or chr(92) in name or ':' in name:
        raise ValueError('invalid name')
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    data = content.encode('utf-8')
    with (root / name).open('xb') as f:
        f.write(data)
    return {'name': name, 'sha256': hashlib.sha256(data).hexdigest()}
