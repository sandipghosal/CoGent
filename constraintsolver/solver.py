from z3 import *


def get_object(id):
    """ Convert a string id to object of type Int """
    __id = Int(id)
    return __id


def weakest_precondition(*args) -> list:
    """ This function derives the weakest precondition
        for a given goal as input parameter """
    goal = Goal()
    for arg in args:
        goal.add(arg)
    t1 = Tactic('simplify')
    t2 = Tactic('solve-eqs')
    t = Then(t1, t2)
    return t(goal)[0]


class Constraint(BoolRef):
    """ Class instantiate a constraint and returns an object of Goal """

    def __init__(self, expression_):
        self.expression = expression_

    def __or__(self, other):
        return Or(self.expression, other)

    def __and__(self, other):
        return And(self.expression, other)

    def __neg__(self):
        return Not(self.expression)

    def __ne__(self, other):
        return Not(self.expression, other)

    def __repr__(self):
        return f'{self.expression}'


