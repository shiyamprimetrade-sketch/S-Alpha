"""Reproducible synthetic acceptance benchmark; run as a module."""
import hashlib
import json
import tempfile
import time
from pathlib import Path
from s_alpha.pipeline import execute
from s_alpha.adaptive import adaptive_repair
from s_alpha.debugging import repair

def benchmark():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        db=root/"db"
        start=time.perf_counter()
        train={"parameters":["a","b"],"expression":["mul","a","b"]}
        result=execute(dict(version=2,id="train",operation="repair",spec=train,candidate=dict(train,expression=["add","a","b"])),root,db)
        if result["status"]!="verified":
            raise RuntimeError("training failed")
        rows=[]
        for i,op in enumerate(("mul","sub","div","mul")):
            spec={"parameters":["x","y"],"expression":[op,["add","x",i+1],"y"]}
            candidate=dict(spec,expression=["add",["add","x",i+1],"y"])
            base=repair(spec,candidate,root/("base"+str(i)))
            learned=adaptive_repair(db,spec,candidate,root/("learned"+str(i)))
            rows.append({"baseline":len(base["attempts"]),"adaptive":len(learned["attempts"]),"baseline_verified":base["status"]=="verified","adaptive_verified":learned["status"]=="verified"})
        baseline=sum(r["baseline"] for r in rows)
        adaptive=sum(r["adaptive"] for r in rows)
        accepted=all(r["adaptive_verified"] and r["baseline_verified"] for r in rows) and adaptive<baseline and all(r["adaptive"]<=r["baseline"] for r in rows)
        artifact=root/"train"/"compute.py"
        return {"cases":rows,"baseline_attempts":baseline,"adaptive_attempts":adaptive,"promotion_allowed":accepted,"artifact_integrity":hashlib.sha256(artifact.read_bytes()).hexdigest()==result["artifact"]["sha256"],"elapsed_seconds":time.perf_counter()-start}

if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2))
