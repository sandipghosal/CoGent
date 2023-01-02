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


x1, x2, p_prime, r = Reals('x1 x2 p_prime r')
g = Goal()
g.add(x1 == r, Or(x1 == p_prime, x2 == p_prime))
t1 = Tactic('simplify')
t2 = Tactic('solve-eqs')
t = Then(t1, t2)
# print(t(g))

gn = Goal()
gn.add(x2 == x1, Or(r == p_prime, x2 == p_prime))
print(t(gn))

