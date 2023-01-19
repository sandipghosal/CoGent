import logging

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
        self.subs = [x[1] for x in subargs]
        self.output = output

    def __repr__(self):
        return self.name + '(' + str(*self.subs) + ') == ' + self.output


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
        self.condition = weakestpre
        self.output = output

    def __repr__(self):
        if self.params:
            # return f'{self.weakestpre} for {self.observer}({self.params}) == {self.output}'
            return str(self.observer) + '(' + str(
                *self.params) + ') == ' + str(
                self.output + '\n')
        else:
            # return f'{self.weakestpre} for {self.observer}() == {self.output}'
            return str(self.observer) + '() == ' + str(
                self.output + '\n')


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


class Contract:
    def __init__(self, target, location, params, registers, constants, precondition, postcondition):
        """
        Hold a contract for a modifier in the form of precondition and postcondition
        :param target: target Method object
        :param location: an object of Location
        :param params: input parameters of target methods and observers
        :param registers: list of registers
        :param constants: list of constants [(id, value),..]
        :param precondition: an object of Precondition
        :param postcondition: object of Postcondition
        """
        self.target = target
        self.location = location
        self.pre = precondition
        self.post = postcondition
        # if self.check(params, registers, constants) == S._unsat():
        #     self.result = S._sat()
        # else:
        #     self.result = S._unsat()
        self.result = self.check(params, registers, constants)
        # obtain precondition from the observers
        # check of precondition => weakestpre is satisfied and store into self.result

    def __repr__(self):
        return 'Location ' + str(self.location) + ' : {' + str(self.pre) + '} ' + self.target.name + '(' + str(*self.target.inparams)+') {' + str(
            self.post) + '} :: ' + str(self.result)

    def check(self, params, registers, constants):
        # Does it satisfy P->Q ?
        # IF there is a solution to Not(P->Q) equiv to (P ^ Not Q) THEN
        #   No
        # ELSE
        #   Yes

        expr = S._implies(self.pre.condition, self.post.condition.weakestpre)

        logging.debug('Checking validity of: ' + str(expr))

        # Do negation of the implication
        # expr = S._and(self.pre.condition, S._neg(self.post.condition.weakestpre))

        # logging.debug('Negation of implication: ' + str(expr))

        # Substitute constants with respective values
        expr = S.do_substitute(expr, constants)

        logging.debug('After constant substitution: ' + str(expr))

        # Add forall parameters
        # expr = S._forall(params, expr)
        # expr = S._forall(registers, expr)

        # logging.debug('After adding for all: ' + str(expr))

        # Add exists registers
        # expr = S._exists(registers, expr)

        params = params + registers

        expr = S._forall(params, expr)

        logging.debug('Final expression before checking validity: ' + str(expr))

        # Check the validity
        result = S.do_check(expr)

        logging.debug('result: '+ str(result))
        return result
