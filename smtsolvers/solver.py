import logging

from z3 import *


def _int(id):
    """ Convert a string id to object of type Int """
    __id = Int(id)
    return __id


def _bool(id):
    """ Convert a string id to object of type Boolean """
    __id = Bool(id)
    return __id


def _boolval(arg):
    return BoolVal(True) if arg == True else BoolVal(False)


def _intval(arg):
    return IntVal(arg)


def _or(first, second):
    """ Returns disjunction of first and second constraints """
    return simplify(Or(first, second))


def _and(first, second):
    """ Returns conjunction of first and second constraints """
    return simplify(And(first, second))


def _neg(first):
    """ Returns negation of the parameter """
    return simplify(Not(first))


def _ne(first, second):
    """ Returns not equal expression of two parameters """
    return simplify(Not(first == second))


def _eq(first, second):
    return first == second


def _lt(first, second):
    return first < second


def _gt(first, second):
    return first > second


def _leq(first, second):
    return first <= second


def _geq(first, second):
    return first >= second


def _implies(antecedent, consequent):
    """ Returns implication where first implies second """
    return simplify(Implies(antecedent, consequent))


def _exists(list_, arg):
    return Exists(list_, arg)


def _forall(list_, arg):
    return ForAll(list_, arg)


def _sat():
    return sat


def _unsat():
    return unsat


def weakest_pre(argv, args) -> list:
    """ This function derives the weakest precondition
        for a given goal as input parameter """
    # if len(args) > 0:
    #     goal = Goal()
    #     goal.add(argv)
    #     goal.add(args[0])
    #     t1 = Tactic('simplify')
    #     # t2 = Tactic('qe')
    #     # t = Then(t1, t2)
    #     print(t1(goal))
    #     return weakest_precondition(*t(goal), args[1:])
    # else:
    #     return argv

    return simplify(substitute(argv, args))


def do_substitute(argv, args):
    return weakest_pre(argv, args)


def do_simplify(argv):
    # simplify using simple simplify() technique
    if argv in (BoolVal(True), BoolVal(False)):
        return argv
    return simplify(argv)


# def do_simplify(argv):
#     # simplify using simple Tactic('ctx-solver-simplify')
#     if argv in (BoolVal(True), BoolVal(False)):
#         return argv
#     g = Goal()
#     g.add(argv)
#     t = Tactic('ctx-solver-simplify')
#     return *t(g)


def do_check(*args):
    s = Solver()
    for argv in args:
        s.add(argv)
    # print(s.model())
    return s.check()


def equivalence(f1, f2):
    fm1 = f1
    fm2 = f2

    if do_check(fm1, Not(fm2)) == unsat:
        return True
    else:
        return False


def check_sat(vars, antecedent, consequent=None):
    # Do negation of the implication
    if consequent is not None:
        expr = _and(antecedent, _neg(consequent))
    else:
        expr = _neg(antecedent)
    logging.debug('Negation of implication: ' + str(expr))
    # Add exists parameters and registers
    if vars != []:
        expr = _exists(vars, expr)
    logging.debug('Final expression before checking SAT: ' + str(expr))
    # Check the validity
    result = do_check(expr)
    return result


def eliminate(argv, args):
    t = Then(Tactic('qe'), Tactic('simplify'), Tactic('solve-eqs'))
    expr = _exists(argv, args)
    logging.debug('Strongest Postcondition: ' + str(expr))
    expr = t(expr).as_expr()
    return expr


def z3reftoStr(argv):
    return obj_to_string(argv)


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


def to_dnf(fml):
    clauses = to_cnf(fml)
    d_clauses = list()
    for c in clauses:
        disjunction = Or([literal if literal.decl().name() != 'Not' else Not(literal.arg(0)) for literal in c])
        d_clauses.append(disjunction)
    dnf = _boolval(False)
    for d in d_clauses:
        dnf = _or(dnf, d)
    print(str(dnf))
