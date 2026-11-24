"""Bounded operator repair for declarative arithmetic candidates."""
from copy import deepcopy
from .synthesis import synthesize, OPS
from .verification import verify_internal_source
from .create import create

def variants(expr, preferences=None):
    if not isinstance(expr,list):
        return
    order = (preferences or {}).get(expr[0], [])
    for op in dict.fromkeys([*order, *OPS]):
        if op!=expr[0]:
            yield [op,deepcopy(expr[1]),deepcopy(expr[2])]
    for left in variants(expr[1], preferences):
        yield [expr[0],left,deepcopy(expr[2])]
    for right in variants(expr[2], preferences):
        yield [expr[0],deepcopy(expr[1]),right]

def repair(spec, candidate, root, expected_cases=(), max_attempts=32, preferences=None):
    if type(max_attempts) is not int or not 1<=max_attempts<=128:
        raise ValueError("invalid attempt limit")
    synthesize(spec)
    if candidate["parameters"]!=spec["parameters"]:
        raise ValueError("parameter mismatch")
    synthesize(candidate)
    expected_cases=list(expected_cases)
    attempts=[]
    def candidates():
        yield candidate["expression"]
        yield from variants(candidate["expression"], preferences)
    for expr in candidates():
        if len(attempts)>=max_attempts:
            break
        source=synthesize(dict(candidate,expression=expr))
        result=verify_internal_source(spec,source,expected_cases)
        attempts.append({"expression":expr,**result})
        if result["status"]=="verified":
            return {"status":"verified","attempts":attempts,"artifact":create(root,"compute.py",source)}
    return {"status":"failed","attempts":attempts}
