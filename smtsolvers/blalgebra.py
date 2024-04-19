import sympy
import z3
import sympy.core as SYMPYC
import sympy.logic.boolalg as SYMPYB
import sympy.logic as SYMPYL
from sympy.logic import simplify_logic
from sympy.core import Expr, Symbol, Number

from sympy.logic.boolalg import And, Or, Not, to_dnf
from z3 import *

# (p1==b0) : a0; contains(p1): a1; contains(b0): a2; isfull(): a3; isempty(): a4

# a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, p1, p2, p3, b0, b1, r1, r2, r3, r4, r5, r6 = sympy.symbols(
#     'a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 p1 p2 p3 b0 b1 r1 r2 r3 r4 r5 r6')

a0, a1, a2, a3, a4, a5, a6, a7, a8, a9 = sympy.symbols(
    'a0 a1 a2 a3 a4 a5 a6 a7 a8 a9')


def _sympy_to_z3(sympy_var_list, sympy_exp):
    """convert a sympy expression to a z3 expression. This returns (z3_vars, z3_expression)"""

    z3_vars = []
    z3_var_map = {}

    for var in sympy_var_list:
        name = var.name
        z3_var = Bool(name)
        z3_var_map[name] = z3_var
        z3_vars.append(z3_var)

    result_exp = _sympy_to_z3_rec(z3_var_map, sympy_exp)

    return result_exp


def _sympy_to_z3_rec(var_map, e):
    """recursive call for sympy_to_z3()"""

    rv = None

    # if not isinstance(e, SYMPYC.Expr):
    #     raise RuntimeError("Expected sympy Expr: " + repr(e))

    if isinstance(e, SYMPYC.Symbol):
        rv = var_map.get(e.name)

        if rv == None:
            raise RuntimeError("No var was corresponds to symbol '" + str(e) + "'")

    elif isinstance(e, SYMPYC.Number):
        rv = int(e)
    elif isinstance(e, SYMPYB.And):
        rv = _sympy_to_z3_rec(var_map, e.args[0])

        for child in e.args[1:]:
            # rv *= _sympy_to_z3_rec(var_map, child)
            rv = z3.And(rv, _sympy_to_z3_rec(var_map, child))
    elif isinstance(e, SYMPYB.Or):
        rv = _sympy_to_z3_rec(var_map, e.args[0])

        for child in e.args[1:]:
            rv = z3.Or(rv, _sympy_to_z3_rec(var_map, child))

    elif isinstance(e, SYMPYB.Not):
        rv = z3.Not(_sympy_to_z3_rec(var_map, e.args[0]))

    if rv == None:
        raise RuntimeError("Type '" + str(type(e)) + "' is not yet implemented for convertion to a z3 expresion. " + \
                           "Subexpression was '" + str(e) + "'.")

    return rv


def sympy_to_z3(expr):
    var_list = list(sympy.symbols(
        'a0 a1 a2 a3 a4 a5 a6 a7 a8 a9'))
    return _sympy_to_z3(var_list, expr)


def simplify(args):
    if args in ('True', 'False'):
        return args
    # expr = SYMPYL.simplify_logic(SYMPYB.to_dnf(args))
    expr = SYMPYB.to_dnf(args, simplify=True)
    # expr1 = sympy_to_z3(expr)
    # expr = SYMPYL.simplify_logic(args)
    return str(expr)
