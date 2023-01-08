from z3 import *


def get_int_object(id):
    """ Convert a string id to object of type Int """
    __id = Int(id)
    return __id


# def get_a_context():
#     """ Returns an instance of Context for building constraint """
#     return Context()


def get_or(first, second):
    """ Returns disjunction of first and second constraints """
    return Or(first, second)


def get_and(first, second):
    """ Returns conjunction of first and second constraints """
    return And(first, second)


def get_neg(first):
    """ Returns negation of the parameter """
    return Not(first)


def get_neq(first, second):
    """ Returns not equal expression of two parameters """
    return Not(first == second)


def get_implies(first, second):
    """ Returns implication where first implies second """
    return Implies(first, second)


def weakest_precondition(argv, args) -> list:
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

def do_simplify(argv):
    return simplify(argv)






