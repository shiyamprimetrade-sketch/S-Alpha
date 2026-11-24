"""Controlled arithmetic source repair experiment; never executes input."""
import ast

def repair_addition(source):
    tree = ast.parse(source)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("unsupported source")
    fn = tree.body[0]
    if fn.name != "add" or ast.dump(fn.args) != ast.dump(ast.parse("def add(a,b): pass").body[0].args) or fn.decorator_list or fn.returns or len(fn.body) != 1:
        raise ValueError("unsupported function")
    ret = fn.body[0]
    if not isinstance(ret, ast.Return) or not isinstance(ret.value, ast.BinOp):
        raise ValueError("unsupported expression")
    expr = ret.value
    if not isinstance(expr.op, (ast.Add, ast.Sub, ast.Mult)) or ast.dump(expr.left) != ast.dump(ast.Name(id="a",ctx=ast.Load())) or ast.dump(expr.right) != ast.dump(ast.Name(id="b",ctx=ast.Load())):
        raise ValueError("unsupported operands")
    changed = not isinstance(expr.op, ast.Add)
    return {"source": "def add(a, b):\n    return a + b\n", "changed": changed}
