import logging

import constraintsolver.solver as S


class Condition:
    def __init__(self, name, condition, output, args=None):
        """
        Atomic unit of pre- and post-condition
        :param name: name of the method or "__equality__"
        :param condition: condition as BoolRef
        :param output: output of if condition is satisfied (true or false)
        :param args: arguments to substitute as a list of tuples [(old, new)]
        """
        self.name = name
        self.guard = S.do_substitute(condition, args) if args else condition
        self.output = output
        self.params = [x[1] for x in args]

    def __repr__(self):
        if self.name == '__equality__':
            return S.boolreftoStr(self.guard)
        else:
            return self.name + '(' + str(*self.params) + ') == ' + self.output


class Postcondition(Condition):
    def __init__(self, name, precondition, output, args=None):
        super().__init__(name=name, condition=precondition, output=output, args=args)



class Precondition:
    def __init__(self, observers, condition):
        """
        Hold each precondition
        :param observers: list of observer objects
        :param condition: condition formed by conjunction of observer objects
        """
        self.observers = observers
        self.condition = S.do_simplify(condition)

    def __repr__(self):
        output = None
        for i in range(len(self.observers)):
            if output:
                output = output + ' and ' + str(self.observers[i])
            else:
                output = str(self.observers[i])
        return output



