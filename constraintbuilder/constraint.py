from z3 import *


class Constraint:
    def __init__(self, arg):
        self.constraint = arg
        self.constraint = self.do_simplify()

    def __repr__(self):
        return f'{self.constraint}'

    def _or(self, other):
        return Constraint(Or(self.constraint, other.constraint))

    def _and(self, other):
        return Constraint(And(self.constraint, other.constraint))

    def _neg(self):
        return Constraint(Not(self.constraint))

    def _ne(self, other):
        return Constraint(Not(self.constraint == other.constraint))

    def _eq(self, other):
        return Constraint(self.constraint == other.constraint)

    def implies(self, other):
        return Constraint(Implies(self.constraint, other.constraint))

    def do_substitute(self, args):
        return self.weakest_pre(args)

    def weakest_pre(self, args):
        """ Obtain weakest precondition
        self: constraint object
        args: tuples of assignments
        """
        return Constraint(substitute(self.constraint, args))

    def do_simplify(self):
        if self.constraint in (BoolVal(True), BoolVal(False)):
            return self.constraint
        else:
            return simplify(self.constraint)


class BoolID(Constraint):
    def __init__(self, arg):
        # val = BoolVal(True) if arg == True else BoolVal(False)
        # return val
        super().__init__(BoolVal(True) if arg == True else BoolVal(False))


class IntID(Constraint):
    def __init__(self, arg):
        # __id = Int(arg)
        # return __id
        super().__init__(Int(arg))
