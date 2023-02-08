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
    return Or(first, second)


def _and(first, second):
    """ Returns conjunction of first and second constraints """
    return And(first, second)


def _neg(first):
    """ Returns negation of the parameter """
    return Not(first)


def _ne(first, second):
    """ Returns not equal expression of two parameters """
    return Not(first == second)


def _eq(first, second):
    return first == second


def _implies(first, second):
    """ Returns implication where first implies second """
    return Implies(first, second)


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

    return substitute(argv, args)


def do_substitute(argv, args):
    return weakest_pre(argv, args)


def do_simplify(argv):
    if argv in (BoolVal(True), BoolVal(False)):
        return argv
    return simplify(argv)


def do_check(*args):
    s = Solver()
    for argv in args:
        s.add(argv)
    return s.check()


def check_sat(params, antecedent, consequent):
    # Do negation of the implication
    expr = _and(antecedent, _neg(consequent))
    logging.debug('Negation of implication: ' + str(expr))
    # Add exists parameters and registers
    expr = _exists(params, expr)
    logging.debug('Final expression before checking SAT: ' + str(expr))
    # Check the validity
    print(expr)
    result = do_check(expr)
    return result


def eliminate(argv, args):
    g = Goal()
    g.add(_exists(argv, args))
    t = Tactic('qe')
    return t(g)[0]


def z3reftoStr(argv):
    return obj_to_string(argv)

