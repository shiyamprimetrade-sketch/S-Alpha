"""Bounded expression-tree synthesis from a declarative specification."""
import ast
import keyword
from .create import create

OPS = {"add":ast.Add,"sub":ast.Sub,"mul":ast.Mult,"div":ast.Div}

def synthesize(spec):
    params = spec["parameters"]
    if not isinstance(params,list) or not 1 <= len(params) <= 8 or any(not isinstance(p,str) or not p.isascii() or not p.isidentifier() or keyword.iskeyword(p) for p in params) or len(set(params)) != len(params):
        raise ValueError("invalid parameters")
    def node(expr, depth=0):
        if depth > 12:
            raise ValueError("expression too deep")
        if type(expr) is int and abs(expr) <= 1000000:
            return ast.Constant(expr)
        if isinstance(expr,str) and expr in params:
            return ast.Name(id=expr,ctx=ast.Load())
        if isinstance(expr,list) and len(expr)==3 and isinstance(expr[0],str) and expr[0] in OPS:
            return ast.BinOp(left=node(expr[1],depth+1),op=OPS[expr[0]](),right=node(expr[2],depth+1))
        raise ValueError("unsupported expression")
    fn = ast.FunctionDef(name="compute",args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=p) for p in params],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[ast.Return(value=node(spec["expression"]))],decorator_list=[])
    tree = ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
    compile(tree,"<synthesis>","exec")
    return ast.unparse(tree)+"\n"

def build_expression(spec, root):
    source = synthesize(spec)
    return {"status":"generated","artifact":create(root,"compute.py",source)}
