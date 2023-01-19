from z3 import *

# x, y = Reals('x y')
#
# g = Goal()
# g.add(x>0, x == y + 2, y>0)
# # print(g)
# t1 = Tactic('simplify')
# t2 = Tactic('solve-eqs')
# t = Then(t1, t2)
# print(t(g))

# for name in tactics():
# t = Tactic('qe')
# print('qe', t.help(), t.param_descrs())


# x1, x2, p_prime, r = Reals('x1 x2 p_prime r')
# g = Goal()
# g.add(x1 == r, Or(x1 == p_prime, x2 == p_prime))
# g.add(False)
# print(g)
# t1 = Tactic('simplify')
# t2 = Tactic('solve-eqs')
# t = Then(t1, t2)
# print(t2(g))
# gn = Goal()
# gn.add(x2 == x1, Or(r == p_prime, x2 == p_prime))
# print(t(gn))

# a = Int('a')
# b = Int('b')
# e = a * b + 3
# print(substitute(e, [(a, b)]))
# print(substitute(e, [(a, z3.IntVal(3))]))

r1, r2, r3, p1, b0 = Ints('r1 r2 r3 p1 b0')
s = Solver()
# s.add(ForAll([p1, b0], And(BoolVal(True), Not(p1 == b0))))
s.add(Exists([p1, b0],ForAll([r1],And(And(r1 == b0, r1 == p1),Not(And(Not(r1 == b0), Not(p1 == b0)))))))
print(s.check())
# print(s.model())

# solve([y == x + 1, ForAll([y], Implies(y <= 0, x < y))])

# simplify()

# s = Solver()
# s.add(Exists([r1, r2, r3], ForAll([b0, p1], And(And(r1 == b0, r1 == p1), Not(Or(r1 == b0, p1 == b0))))))
# print(s.check())

# s.add(True, I_push_p1 == I_contains_p1)
# print(s.check())

# s.add(Implies(r1 == I_contains_p1, Or(I_push_p1==I_contains_p1, r1==I_contains_p1)))
# print(s.check())
