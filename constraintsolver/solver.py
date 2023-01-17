from z3 import *


def _int(id):
    """ Convert a string id to object of type Int """
    __id = Int(id)
    return __id


def _bool(arg):
    return BoolVal(True) if arg == True else BoolVal(False)


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
