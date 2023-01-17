import constraintsolver.solver as S


class Observer:
    def __init__(self, name, condition, output, subargs=None):
        """
        Holds the attribute for an observer method
        :param name: name of the observer method
        :param condition: guard condition, an object of Constraint
        :param output: output of the observer method
        :param subargs: list of tuples to substitute (oldparam, newparam)
        """
        self.name = name
        print(type(condition))
        if subargs:
            self.guard = S.do_substitute(condition, subargs)
        else:
            self.guard = condition
        self.subs = subargs
        self.output = output

    def __repr__(self):
        return f'{self.name}:{self.guard}:{self.output}'


class WeakestPrecondition:
    def __init__(self, args):
        """
        Calculate and holds weakest precondition at a location
        :param args: list of tuples (transition, postobserver) where
        transition and postobserver are objects of Transition and Observer respectively
        """
        self.weakestpre = S.do_simplify(S._and(self.get_disjunction(args),
                                               self.get_implication(args)))

    def __repr__(self):
        return f'{self.weakestpre}'

    def get_disjunction(self, args):
        """
        Obtain disjunction of all the constraints for the list of transitions
        :param args: list of tuples (transition, postobserver)
        :return: Constraint object, disjunction of all constraints for the transitions
        """
        result = None

        for index in range(len(args)):
            if index == 0:
                # for first index get the z3 constraint
                result = (args[index][0]).guard
            else:
                # for next transition do OR with previous results
                result = S._or(result, (args[index][0]).guard)

        return result

    def get_implication(self, args):
        """
        Derive the conjunction of implications: from transition to postobserver
        then the guard of the observer should hold
        :param args: list of tuples (transition, postobserver)
        :return: Constraint object, conjunction of all implications
        """
        result = None
        # for each of the tuple in the list
        for index in range(len(args)):
            wp = S.weakest_pre(args[index][1].guard, args[index][0].assignments)
            if index == 0:
                result = S._implies(args[index][0].guard, wp)
            else:
                result = S._and(result, S._implies(args[index][0].guard, wp))
        return result


class Postcondition:
    def __init__(self, weakestpre, observername, params, output):
        """
        Holds the attribute for an observer method
        :param observer: object of Observer class
        :param weakestpre: object of WeakestPrecondition class
        """
        self.observer = observername
        self.params = params
        self.weakestpre = weakestpre
        self.output = output

    def __repr__(self):
        if self.params:
            return f'WP:{self.weakestpre} FOR {self.observer}({self.params}) == {self.output}'
        else:
            return f'WP:{self.weakestpre} FOR {self.observer}() == {self.output}'


class Contract:
    def __init__(self, observers, weakestpre):
        """
        Hold a contract for a modifier in the form of precondition and postcondition
        :param observers: list of Observers objects
        :param weakestpre: object of WeakestPrecondition
        """
        self.observers = observers
        self.weakestpre = weakestpre
        # obtain precondition from the observers
        # check of precondition => weakestpre is satisfied and store into self.result

    def get_pre(self):
        pass
