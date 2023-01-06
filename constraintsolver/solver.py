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


class Constraint(Z3PPObject):
    """ Class instantiate a constraint and returns an object of Goal """
    def __new__(self, expression_=None):
        self.expression = Goal()
        if expression_ is not None: self.expression.add(expression_)
        return self.expression

    def __repr__(self):
        return f'{self.expression}'

    # def __add__(self, other):
    #     return self.expression.add(other)
