"""Bounded calculator demo; no eval or user-supplied code."""
from decimal import Decimal, InvalidOperation, localcontext
import operator
OPS={"+":operator.add,"-":operator.sub,"*":operator.mul,"/":operator.truediv}
def calculate(a,op,b):
    if not isinstance(op,str) or op not in OPS:
        raise ValueError("unsupported operator")
    def number(v):
        if not isinstance(v,str) or not 1<=len(v)<=64:
            raise ValueError("invalid number")
        try:
            n=Decimal(v)
        except InvalidOperation as exc:
            raise ValueError("invalid number") from exc
        if not n.is_finite() or abs(n)>Decimal("1e12") or abs(n.as_tuple().exponent)>24:
            raise ValueError("number out of bounds")
        return n
    x,y=number(a),number(b)
    if op=="/" and not y:
        raise ValueError("division by zero")
    with localcontext() as ctx:
        ctx.prec=28
        return str(OPS[op](x,y))
