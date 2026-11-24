"""Learn operator preferences from verified repair observations."""
from collections import Counter, defaultdict
from .knowledge import observations
from .debugging import repair
from .synthesis import OPS

def changes(before,after):
    if isinstance(before,list) and isinstance(after,list) and len(before)==len(after)==3:
        if before[0]!=after[0]:
            yield before[0],after[0]
        yield from changes(before[1],after[1])
        yield from changes(before[2],after[2])

def preferences(db):
    counts=defaultdict(Counter)
    for row in observations(db):
        result=row["result"]
        if result["status"]!="verified":
            continue
        for old,new in changes(row["candidate"]["expression"],result["attempts"][-1]["expression"]):
            if old in OPS and new in OPS:
                counts[old][new]+=1
    return {old:sorted(counter,key=lambda op:(-counter[op],op)) for old,counter in counts.items()}

def adaptive_repair(db,spec,candidate,root,expected_cases=(),max_attempts=32):
    return repair(spec,candidate,root,expected_cases,max_attempts,preferences(db))
