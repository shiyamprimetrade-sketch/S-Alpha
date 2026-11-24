"""Local Fusion dispatch; legacy v2 remains unchanged."""
from pathlib import Path
import re
import sqlite3
from .pipeline import execute
from .fusion_calculator import calculate
from .fusion_website import build_website
from .fusion_inventory import Inventory
from .fusion_repair import repair_demo,knowledge

DEFAULT_PORT=8767

def dispatch(task,root,db):
    if isinstance(task,dict) and type(task.get("version")) is int and task["version"]==2:
        return execute(task,root,db)
    ident=task.get("id") if isinstance(task,dict) else None
    result={"version":3,"id":ident if isinstance(ident,str) else None}
    def fail(code):
        return dict(result,status="failed",error={"code":code})
    if not isinstance(task,dict) or type(task.get("version")) is not int or task["version"]!=3 or not isinstance(ident,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",ident):
        return fail("INVALID_TASK")
    op=task.get("operation")
    args=task.get("args",{})
    if not isinstance(args,dict):
        return fail("INVALID_ARGS")
    try:
        if op=="calculator":
            data={"value":calculate(**args)}
        elif op=="website":
            out=Path(root)/ident
            if out.is_symlink():
                return fail("UNSAFE_WORKSPACE")
            data=build_website(args,out)
        elif op in ("inventory_register","inventory_adjust","inventory_search"):
            inv=Inventory(db)
            if op=="inventory_register":
                inv.register(**args)
                data={"registered":True}
            elif op=="inventory_adjust":
                data={"quantity":inv.adjust(**args)}
            else:
                data={"products":inv.search(**args)}
        elif op=="repair_demo":
            data=repair_demo(db,**args)
        elif op=="fusion_knowledge":
            if args:
                return fail("INVALID_ARGS")
            data=knowledge(db)
        else:
            return fail("INVALID_OPERATION")
        return dict(result,status="ok" if data.get("status")!="failed" else "failed",data=data)
    except (ValueError,TypeError,KeyError,OverflowError):
        return fail("INVALID_ARGS")
    except sqlite3.Error:
        return fail("STORAGE_ERROR")
    except OSError:
        return fail("IO_ERROR")
