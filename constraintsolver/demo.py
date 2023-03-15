# from z3 import *
#
# a0, a1, a2, a3, a4 = Bools('a0 a1 a2 a3 a4')
# #
# # simple simplify()
# # print('simple simplification')
# # print(simplify(Implies(And(Or(a0, a1), Not(a3)), a2)))


#
# g = Goal()
# g.add(And(Or(Not(a3), Not(And(Not(a3), Not(a4)))), Or(a3, Not(And(a3, Not(a4))))))
#
# # simplify using Tactic 'ctx-simplify'
# print('simplification using ctx-simplify')
# t1 = Tactic('ctx-simplify')
# print(t1(g))
#
# # simplify using Tactic 'ctx-solver-simplify'
# print('simplification using ctx-solver-simplify')
# t2 = Tactic('ctx-solver-simplify')
# print(t2(g))
#
# # simplify using Tactic 'solver-subsumption'
# print('simplification using solver-subsumption')
# t3 = Tactic('solver-subsumption')
# print(t3(g))
#
# # simplify using Tactic 'solver-subsumption'
# print('simplification using unit-subsume-simplify')
# t4 = Tactic('unit-subsume-simplify')
# print(t4(g))
#
#
# #
# # print('\n\n Split cause:')
# # t3 = Tactic('split-clause')
# # print(t3(g))
#
#
# def is_atom(t):
#     if not is_bool(t):
#         return False
#     if not is_app(t):
#         return False
#     k = t.decl().kind()
#     if k == Z3_OP_AND or k == Z3_OP_OR or k == Z3_OP_IMPLIES:
#         return False
#     if k == Z3_OP_EQ and t.arg(0).is_bool():
#         return False
#     if k == Z3_OP_TRUE or k == Z3_OP_FALSE or k == Z3_OP_XOR or k == Z3_OP_NOT:
#         return False
#     return True
#
#
# def atoms(fml):
#     visited = set([])
#     atms = set([])
#
#     def atoms_rec(t, visited, atms):
#         if t in visited:
#             return
#         visited |= {t}
#         if is_atom(t):
#             atms |= {t}
#         for s in t.children():
#             atoms_rec(s, visited, atms)
#
#     atoms_rec(fml, visited, atms)
#     return atms
#
#
# def atom2literal(m, a):
#     if is_true(m.eval(a)):
#         return a
#     return Not(a)
#
#
# def implicant(atoms, s, snot):
#     m = snot.model()
#     lits = [atom2literal(m, a) for a in atoms]
#     is_sat = s.check(lits)
#     assert is_sat == unsat
#     core = s.unsat_core()
#     return Or([mk_not(c) for c in core])
#
#
# def to_cnf(fml):
#     atms = atoms(fml)
#     s = Solver()
#     snot = Solver()
#     snot.add(Not(fml))
#     s.add(fml)
#
#     while sat == snot.check():
#         clause = implicant(atms, s, snot)
#         yield clause
#         snot.add(clause)
#
#
# # fml = And(Or(a0, Not(And(Not(a3), a4))), Or(a0, a2, Not(And(Not(a3), Not(a4)))), Or(a2, Not(And(a3, Not(a4)))))
# fml = Or(And(Not(a0), Not(a1)), And(Not(a2), Not(a3)))
# for clause in to_cnf(fml):
#     print(clause)
#     pass




############ SIMPLIFICATION USING SYMPY #################
import sympy
from sympy.logic.boolalg import And, Or, Not, to_dnf

# (p1==b0) : a0; contains(p1): a1; contains(b0): a2; isfull(): a3; isempty(): a4

a0, a1, a2, a3, a4 = sympy.symbols('a0 a1 a2 a3 a4')
#
# precondition for isfull():
# f = And(Or(Not(a3), Not(And(Not(a3), Not(a4)))), Or(a3, Not(And(a3, Not(a4)))))
# print(f)
# print(sympy.logic.simplify_logic(f))
# Produces: True :: a4 :: isempty()

# precondition for Not(isempty()):
# f = And(Or(Not(a3),Not(And(Not(a3), a4))), Or(Not(a3), Not(And(Not(a3),Not(a4)))), Or(a3, Not(And(a3, Not(a4)))))
# print(f)
# print(sympy.logic.simplify_logic(f))
# Produces: True :: a4 :: isempty()

# #
# precondition for contains(b0):
# f = And(Or(a0, Not(And(Not(a3), a4))), Or(a0, a2, Not(And(Not(a3), Not(a4)))), Or(a2, Not(And(a3, Not(a4)))))
# print(f)
# print(sympy.logic.simplify_logic(f))
# Produces: (a3 and a4) or (a0 and Not(a3)) or (a2 and Not(a4)) :: (isfull() and isempty()) or ((p1 == b0) and Not(isfull())) or (contains(b0) and Not(isempty()))


# # precondition for Not(contains(b0)):
# f = And(Or(Not(a0), Not(And(Not(a3), a4))), Or(Not(And(Not(a3), Not(a4))), And(Or(a1, Not(a2)), Not(a0))), Or(Not(a2), Not(And(a3, Not(a4)))))
# print(f)
# print(sympy.logic.simplify_logic(f))
# # print(to_dnf(f))
# # Produces: (a3 and a4) or (a3 and Not(a2)) or (a4 and Not(a0)) or (Not(a0) and Not(a2)) or (a1 and Not(a0) and Not(a3))
# # :: (isfull() and isempty()) or (isfull() and Not(contains(b0)) or (isempty() and Not(p1 == b0)) or (Not(p1 == b0) and Not(contains(b0))) or (contains(p1) and Not(p1 == b0) and Not(isfull())))



# Some Extra Formula
# f = (((Not(a0) and a1) or (Not(a0) and Not(a2))) and Not(a0) and Not(a2))
# f = And(Or(And(Not(a0), a1), And(Not(a0), Not(a2))), Not(a0), Not(a2))
# print(f)
# print(sympy.logic.simplify_logic(f))


##################  END  #################################




############ SIMPLIFICATION USING PYEDA #################
#
# from pyeda.boolalg.expr import exprvar
# from pyeda.boolalg.minimization import espresso_exprs
#
# a, b, c, d, e = map(exprvar, 'abcde')
#
# f = (a | ~(e & ~d)) & (c | ~(d & ~e)) & (a | c | ~(~d & ~e))
#
# f1m, = espresso_exprs(f.to_dnf())
# print(f1m)
##################  END  #################################