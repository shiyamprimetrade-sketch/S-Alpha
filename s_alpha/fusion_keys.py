"""Persistent local signing key; trusted private directory required."""
import os
import secrets
import stat
from pathlib import Path

def load_key(path):
    path=Path(path)
    flags=os.O_RDONLY|getattr(os,"O_NOFOLLOW",0)|getattr(os,"O_BINARY",0)
    try:
        fd=os.open(path,flags)
    except FileNotFoundError:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_BINARY",0),0o600)
        with os.fdopen(fd,"wb") as f:
            f.write(secrets.token_bytes(32))
            f.flush()
            os.fsync(f.fileno())
        fd=os.open(path,flags)
    with os.fdopen(fd,"rb") as f:
        info=os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or (os.name=="posix" and info.st_mode & 0o077):
            raise ValueError("unsafe key file")
        key=f.read(33)
    if len(key)!=32:
        raise ValueError("invalid key file; restore original key")
    return key
