"""Functional checks for internally synthesized arithmetic programs only."""
import itertools
import math
import operator
from .synthesis import synthesize
from .create import create

REFERENCE = {"add":operator.add,"sub":operator.sub,"mul":operator.mul,"div":operator.truediv}

def reference(expr, env):
    if type(expr) is int:
        return expr
    if isinstance(expr,str):
        return env[expr]
    op,left,right=expr
    return REFERENCE[op](reference(left,env),reference(right,env))

def outcome(fn):
    try:
        return ("value",fn())
    except ZeroDivisionError:
        return ("division_by_zero",None)

def equal(a,b):
    if a[0]!=b[0]:
        return False
    if a[0]!="value":
        return True
    if type(a[1]) is int and type(b[1]) is int:
        return a[1]==b[1]
    return math.isclose(a[1],b[1],rel_tol=1e-12,abs_tol=1e-12)

def cases(n):
    # Cover each parameter independently and correlated boundary inputs.
    yield from ((v,)*n for v in (-10,-1,0,1,10))
    for i,v in itertools.product(range(n),(-7,0,3)):
        args=[1]*n
        args[i]=v
        yield tuple(args)

def verify(spec, expected_cases=()):
    source=synthesize(spec)
    ns={}
    exec(compile(source,"<internal synthesis>","exec"),{"__builtins__":{}},ns)
    fn=ns["compute"]
    failures=[]
    total=0
    for args in cases(len(spec["parameters"])):
        env=dict(zip(spec["parameters"],args))
        expected=outcome(lambda:reference(spec["expression"],env))
        actual=outcome(lambda:fn(*args))
        total+=1
        if not equal(expected,actual):
            failures.append({"args":args,"expected":expected,"actual":actual})
    for args,value in expected_cases:
        if len(args)!=len(spec["parameters"]) or any(type(x) is not int or abs(x)>1000000 for x in args) or type(value) not in (int,float):
            raise ValueError("invalid expected case")
        actual=outcome(lambda:fn(*args))
        total+=1
        if not equal(("value",value),actual):
            failures.append({"args":args,"expected":("value",value),"actual":actual})
    return {"status":"failed" if failures else "verified","total":total,"passed":total-len(failures),"failures":failures}

def build_verified(spec,root,expected_cases=()):
    result=verify(spec,expected_cases)
    if result["status"]=="verified":
        result["artifact"]=create(root,"compute.py",synthesize(spec))
    return result
