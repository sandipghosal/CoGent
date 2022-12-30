from z3 import *

# x = Int('x')
# y = Int('y')

x1 = Int('x1')
x2 = Int('x2')
p_prime = Int('p_prime')
r = Int('r')

weakestp = Goal()

# weakestp.add(Exists([y], And(y == x+1, y == 5)))
# t = Tactic('qe')

# weakestp.add(And(y == x+1, y==5))
weakestp.add(Exists([x1,x2], And(x1 == r, x2 == x1, Or(x1 == p_prime, x2 == p_prime))))
t = Tactic('qe')

wp = t(weakestp)

print(wp)




# s = Solver()
#
# try:
#     f = open("read.txt", "r")
#     try:
#         for l in f:
#             s.add(eval(l))
#     finally:
#         f.close()
# except IOError:
#     pass

# print(s.check())
# print(s.model())