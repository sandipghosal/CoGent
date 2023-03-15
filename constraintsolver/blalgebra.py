import sympy
from sympy.logic import simplify_logic
from sympy.logic.boolalg import And, Or, Not, to_dnf

# (p1==b0) : a0; contains(p1): a1; contains(b0): a2; isfull(): a3; isempty(): a4

a0, a1, a2, a3, a4, a5, a6 = sympy.symbols('a0 a1 a2 a3 a4 a5 a6')

def simplify(args):
    if args in ('True', 'False'):
        return args
    expr = sympy.simplify_logic(args)
    return str(expr)