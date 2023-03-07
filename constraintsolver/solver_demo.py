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


r1, r2, r3, p1, b0, b1 = Ints('r1 r2 r3 p1 b0 b1')

# s.add(Exists([p1, b0],ForAll([r1],And(And(r1 == b0, r1 == p1),Not(And(Not(r1 == b0), Not(p1 == b0)))))))
# g = Goal()
# g.add(Exists([r1, r2], Or(p1 == b0, r1 == b0)))
# print(g)
# t = Tactic('qe')
# print(t(g))

# print(s.check())


# print(obj_to_string(Exists([r1, r2], Or(r1 == b0, r2 == b0))))

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

# print(substitute(Or(r1 == b0, r2 == b0), [(r1, p1), (r2, r1)]))

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


a0, a1, a2, a3, a4 = Bools('a0 a1 a2 a3 a4')


# simple simplify()
# print(simplify(Or(True, a1)))

# g = Goal()
# g.add(And(a0, Not(And(a1, a0))))
# g.add(And(Or(a2, Not(a0)), Or(Not(a2), Not(And(Not(a0), a1))), Or(Not(a2), Not(And(Not(a0), Not(a2))))))

# simplify using Tactic 'ctx-simplify'
# t1 = Tactic('ctx-simplify')
# print(t1(g))

# simplify using Tactic 'ctx-solver-simplify'
# t2 = Tactic('ctx-solver-simplify')
# print(t2(g))
#
# print('\n\n Split cause:')
# t3 = Tactic('split-clause')
# print(t3(g))


def is_atom(t):
    if not is_bool(t):
        return False
    if not is_app(t):
        return False
    k = t.decl().kind()
    if k == Z3_OP_AND or k == Z3_OP_OR or k == Z3_OP_IMPLIES:
        return False
    if k == Z3_OP_EQ and t.arg(0).is_bool():
        return False
    if k == Z3_OP_TRUE or k == Z3_OP_FALSE or k == Z3_OP_XOR or k == Z3_OP_NOT:
        return False
    return True


def atoms(fml):
    visited = set([])
    atms = set([])

    def atoms_rec(t, visited, atms):
        if t in visited:
            return
        visited |= {t}
        if is_atom(t):
            atms |= {t}
        for s in t.children():
            atoms_rec(s, visited, atms)

    atoms_rec(fml, visited, atms)
    return atms


def atom2literal(m, a):
    if is_true(m.eval(a)):
        return a
    return Not(a)


def implicant(atoms, s, snot):
    m = snot.model()
    lits = [atom2literal(m, a) for a in atoms]
    is_sat = s.check(lits)
    assert is_sat == unsat
    core = s.unsat_core()
    # return Or([mk_not(c) for c in core])
    return Or([mk_not(c) for c in core])


def to_cnf(fml):
    atms = atoms(fml)
    s = Solver()
    snot = Solver()
    snot.add(Not(fml))
    s.add(fml)

    while sat == snot.check():
        clause = implicant(atms, s, snot)
        yield clause
        snot.add(clause)


a, b, c, = Bools('a b c')
# fml = And(Or(a2, Not(a0)), Or(Not(a2), Not(And(Not(a0), a1))), Or(Not(a2), Not(And(Not(a0), Not(a2)))))
fml = Or(And(a, b), And(Not(a), c))
# fml = Or(a2, And(Not(a1),Not(a3)))

for clause in to_cnf(fml):
    print(clause)
    pass
