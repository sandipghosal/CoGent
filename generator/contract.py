import copy
import itertools
import logging

import constraintsolver.solver as SOLVER
import constraintsolver.MUS as MUS
import constraintsolver.blalgebra as SIMPLIFIER
from conditionbuilder.condition import Condition
from ramodel.config import Monomial
import ramodel.automaton as ra

automaton = None
location = None
wp = None


class Contract:
    def __init__(self, precondition, target, postcondition, result=None):
        """
        Hold a contract for a location
        :param monomial: Object of Monomial class that serves the precondition
        :param observer: Object of Observer class that serves the postcondition
        :param result: Result True/False representing a valid or invalid contract
        """
        self.pre = precondition
        self.target = target
        self.post = postcondition
        if result is not None:
            self.result = result
        else:
            self.result = self.check()

    def __eq__(self, other):
        # if the both the contracts are referring the same instance
        if id(self) == id(other):
            return True
        # if pre- or post-conditions are different
        elif self.pre != other.pre or self.post != other.post:
            return False
        # if the result of the contracts are different
        elif self.result != other.result:
            return False
        else:
            return True

    def __hash__(self):
        return hash(str(self.pre.monomials) + str(self.post.monomials))

    def __repr__(self):
        return str(self.pre) + ' ' + str(self.target) + ' ' + str(self.post) + ' :: ' + str(self.result)

    def __or__(self, other):
        """
        Perform join operation of two contracts
        :param other:
        :return:
        """
        self.pre = self.pre & other.pre
        if self.post != other.post:
            self.post = self.post | other.post

        # following code was written to check if any other parameter than b0 is involved
        # if not then change the target input parameter to b0 only
        # -- not a good implementation: hence commenting
        # inputs = set()
        # for monomial in self.pre.monomials:
        #     for observer in monomial.observers:
        #         {inputs.add(x) for x in observer.method.inputs}
        # inputs = list(inputs)
        # if len(inputs) == 1:
        #     self.target.inputs = inputs
        # else:
        #     self.target.inputs = automaton.TARGET.inputs

        self.target.inputs = automaton.TARGET.inputs
        return self

    def __and__(self, other):
        """
        Perform meet of two contracts
        :param other:
        :return:
        """
        self.pre = self.pre | other.pre
        # if the postconditions are same perform the disjunction of preconditions
        if self.post != other.post:
            self.post = self.pre.implies(self.post) & other.pre.implies(other.post)
        # gather the paramaters from monomials in precondition
        inputs = set()
        for monomial in self.pre.monomials:
            for observer in monomial.observers:
                {inputs.add(x) for x in observer.method.inputs}
        inputs = list(inputs)
        # if all monomials depends on a single parameter set the same a parameter for target
        # otherwise use the parameter of target from configuration
        if len(inputs) == 1:
            self.target.inputs = inputs
        else:
            self.target.inputs = automaton.TARGET.inputs

        return self

    def apply_equalities(self):
        """
        apply equalities in a contract: check if the equalities are true then convert (b0 == p1) to (b0) only
        :return:
        """
        flag = False
        for monomial in self.pre.monomials:
            for first in monomial.observers:
                if first.method.name.find('__equality__') != -1 and first.output == automaton.OUTPUTS['TRUE']:
                    first.method.guard = SOLVER.do_substitute(first.method.guard, monomial.substitutes)
                    # first.method.inputs = [S.z3reftoStr(monomial.substitutes[0][1])]
                    flag = True

                    # hard code hack for the time being
                    automaton.LITERALS[first] = 'a0'

                    for second in monomial.observers:
                        if second.method.name.find('__equality__') != -1 or id(first) == id(second):
                            continue
                        if first.method == second.method and first.method.guard == SOLVER.do_substitute(
                                second.method.guard,
                                monomial.substitutes):
                            logging.debug('For monomial:' + str(monomial))
                            logging.debug(str(first) + ' == ' + str(second))
                            logging.debug('Removing observer: ' + str(second))
                            monomial.remove(second)
        return flag

    def check(self):
        # Does it satisfy P->Q ?
        # IF there is a solution to Not(P->Q) equiv to (P ^ Not Q) THEN
        #   unsat
        # ELSE
        #   no

        params = set()
        constants = list()
        # gather the constants for substitution
        for c, k in automaton.CONSTANTS:
            constants.append((SOLVER._int(c), SOLVER._intval(k)))

        # gather all the registers and parameters
        for monomial in self.pre.monomials:
            for observer in monomial.observers:
                for x in observer.method.inputs:
                    params.add(SOLVER._int(x))

        for r in (*automaton.REGISTERS, *automaton.TARGET.inputs):
            params.add(SOLVER._int(r))

        # Substitute constants with respective values
        pre = SOLVER.do_substitute(self.pre.condition, constants)
        post = SOLVER.do_substitute(self.post.condition, constants)

        logging.debug('Checking SAT for: ' + str(pre) + ' => ' + str(post))

        # Check the validity
        result = SOLVER.check_sat(vars=list(params), antecedent=pre, consequent=post)

        logging.debug('result: ' + str(result) + '\n')

        if result == SOLVER._sat():
            return False
        else:
            return True


def remove_invalids(contracts):
    contracts[:] = [x for x in contracts if x.result]
    return contracts


def get_substitutes(observer):
    substitute = list()
    # substitute.append((S._int(observer.method.inputs[0]), S._int(observer.method.inputs[1])))
    if len(observer.method.inputs) <= 1:
        return substitute
    for item in (automaton.TARGET.inputs or automaton.TARGET.outputs):
        for i in range(len(observer.method.inputs)):
            if i == 0:
                other = observer.method.inputs[i + 1]
            else:
                other = observer.method.inputs[i - 1]

            if item == observer.method.inputs[i]:
                # substitute.append((S._int(item), S._int(other)))
                substitute.append((SOLVER._int(other), SOLVER._int(item)))
    # observer.method.guard = S.do_substitute(observer.method.guard, substitute)
    # observer.method.inputs = [S.z3reftoStr(substitute[0][1])]
    return substitute


def update_post_param(contract):
    """
    Example: Change postcondition from contains(b0) to contains(p1) when (p1==b0) is enforced and
    no other observer is in the precondition that accepts a parameter
    :param contract:
    :return:
    """
    substitutes = contract.pre.monomials[0].substitutes

    for monomial in contract.pre.monomials:
        for observer in monomial.observers:
            # continue with updating postparameter only if
            # there is no observer having a input paramater in the precondition
            if observer.method.name.find('__equality__') != -1 \
                    and observer.output == automaton.OUTPUTS['TRUE']:
                continue
            elif observer.method.name.find('__equality__') != -1 \
                    and observer.output == automaton.OUTPUTS['FALSE']:
                return contract
            elif observer.method.inputs:
                return contract
            else:
                continue
    # there must be only one monomial and one observer
    assert len(contract.post.monomials) == 1
    assert len(contract.post.monomials[0].observers) == 1

    observer = contract.post.monomials[0].observers[0]
    # update the parameter in the postcondition
    for i in range(len(substitutes)):
        param = SOLVER.z3reftoStr(substitutes[i][0])
        for j in range(len(observer.method.inputs)):
            if observer.method.inputs[j] == param:
                observer.method.inputs[j] = SOLVER.z3reftoStr(substitutes[i][1])
    contract.post.monomials[0].observers[0] = observer
    contract.post.update(automaton)
    return contract


def get_observer(observers, constraint):
    for x in observers:
        if MUS.isequal(constraint, x.method.guard):
            return copy.deepcopy(x)


def create_monomial(observers, constraint=None):
    """
    Create an object of Monomial for a given list of observers and constraints (if given any)
    :param observers: list of Observer objects
    :param constraint: containing list of clauses
    :return: a list of Monomial objects
    """
    if constraint:
        obs = list()
        for c in constraint:
            if str(c) == 'True':
                obs.append(create_observer('True', SOLVER._boolval(True)))
            elif str(c) == 'False':
                obs.append(create_observer('False', SOLVER._boolval(False)))
            else:
                obs.append(get_observer(observers, c))
        monomial = Monomial(obs)
    else:
        monomial = Monomial(observers)
    return monomial


def prepare_condition(observers, constraint=None):
    monomial = create_monomial(observers, constraint)
    condition = Condition([monomial], automaton)
    return condition


def create_observer(name, guard):
    """
    Create an observer object for True or False value
    :return: observer object
    """
    method = ra.Method(name)
    method.guard = guard
    method.inputs = list()
    method.outputs = list()
    output = automaton.OUTPUTS['TRUE'] if method.name == 'True' else automaton.OUTPUTS['FALSE']
    observer = ra.Observer(method=method, output=output)
    return observer


def crate_contracts(observers, constraints=None):
    contracts = list()

    # if the set of constraint is blank then
    # we can just add a contract like {True} push(p1){wp}
    if not constraints:
        if str(wp.method.guard) == 'False':
            observer = create_observer('False', wp.method.guard)
        else:
            observer = create_observer('True', wp.method.guard)

        pre = prepare_condition([observer])
        post = prepare_condition([copy.deepcopy(wp)])
        contract = Contract(pre, copy.deepcopy(automaton.TARGET), post, True)
        contracts.append(contract)

    else:
        for c in constraints:
            pre = prepare_condition(observers, c)
            post = prepare_condition([copy.deepcopy(wp)])
            # create a contract
            contract = Contract(pre, copy.deepcopy(automaton.TARGET), post, True)
            contracts.append(contract)

    return contracts


def remove_redundants(subsets):
    """
    Remove redundants elements (lists) from the subsets
    :param subsets: list of lists: all possible proper subsets
    :return: list of lists: list must contain all unique lists
    """
    indices = list()
    for i in range(len(subsets) - 1):
        for j in range(i + 1, len(subsets)):
            if MUS.equalMUSes(subsets[i], subsets[j]):
                indices.append(j)
    if indices:
        temp = list()
        for i in range(len(subsets)):
            if i not in indices:
                temp.append(subsets[i])
        # subsets[:] = [subsets.pop(i) for i in indices]
        subsets = temp
    return subsets


# def findsubsets(muses):
#     subsets = list()
#     # find all proper subsets of maximum length n-1
#     for m in muses:
#         for i in range(1, len(m) - 1):
#             subsets.append(itertools.combinations(m, i))
#     return subsets


def refine(muses, condition):
    """
    Enforce different constraints on each MUS and filter based on them
    :param muses: list of lists: all possible MUSes
    :param condition: weakest precondition
    :return: list of lists: list of all possible satisfiable subsets where wp is a member of each subset
    """
    # remove redundant subsets
    subsets = remove_redundants(muses)

    # Enforce other restrictions based on the requirements
    # such as ensure two equalities in the precondition for the modifier accepting two parameters
    return subsets


def get_MUSes(conditions):
    """
    Obtain all possible Minimum Unsatisfiable Subsets (MUS) for a list of conditions
    :param conditions: list of conditions derived from observer methods at pre-state
    :return: list of lists: list of all possible unsatisfiable subsets where wp is not a member
    """
    # obtain the negation of weakest precondition (wp)
    clause = SOLVER._neg(wp.method.guard)
    # supply Not(wp) as one of the conditions for obtaining MUS
    muses = MUS.generate(conditions, clause)
    if not muses:
        return []
    else:
        # enforce some constraints on the muses as per need
        return refine(muses, clause)


def substitute_inputs(fmethod, tmethod):
    """
    Replace inputs of fmethod by the inputs of tmethod, e.g., change contains(p1) to contains(b0)
    and the method guard as well, e.g., (r1==p1) to (r1==b0)
    :param fmethod: the initial method which needs to be replaced
    :param tmethod: the target method
    :return: the target method object
    """
    if str(fmethod.guard) in ['True', 'False']:
        tmethod.guard = fmethod.guard
        return tmethod
    assert len(fmethod.inputs) == len(tmethod.inputs) == 1
    subs = [(SOLVER._int(fmethod.inputs[0]), SOLVER._int(tmethod.inputs[0]))]
    tmethod.guard = SOLVER.do_substitute(fmethod.guard, subs)
    return tmethod


def check_subset(muses):
    for m in muses:
        result = True
        for i in range(len(m)):
            result = SOLVER._and(result, m[i])
        output = "%s %s" % (str(m), SIMPLIFIER.simplify(str(result)))
        logging.debug(output)



def get_conditions(observers):
    """
    Collect the conditions respective to the list of given observers
    :param observers: list of observers
    :return: list of conditions
    """
    conditions = set()
    for o in observers:
        conditions.add(o.method.guard)
    return list(conditions)


def observers():
    """ Prepare the set of observers by filtering the symbols for the current location.
    Filtering enforces some requirements such as removing redundant observer methods.
    For example, contains(p1) maybe removed when contains(b0) is present.
    """
    observers = list()

    for k, v in automaton.SYMBOLS:
        # first check if the symbol is relevant
        # search transitions at current location corresponding to the method k and output v
        # if transition found then collect the method create an observer and add into the observer list
        if k.name.find('__equality__') != -1:
            # if both the modifier and post state query are not parameterized then no need to
            # add equality
            if not (automaton.TARGET.inputs and wp.method.inputs):
                continue
            # if an equality then no need to search for transition and add into conditions and symbols list directly
            m = copy.deepcopy(k)
            o = ra.Observer(method=m, output=automaton.OUTPUTS[v])
            o.literal = automaton.LITERALS[o]
        else:
            # do not consider the same query in the pre that is there in post with same parameter
            # if k == wp.method and k.inputs != wp.method.inputs:
            #     continue

            trans = location.get_transitions(destination=location,
                                             method=k,
                                             output=automaton.OUTPUTS[v])
            assert len(trans) <= 1
            # if no transition found then continue
            if len(trans) == 0:
                continue
            # make a separate instance of the symbol method
            m = copy.deepcopy(k)
            # if the queried contains(b0)==True but returned transition for contains(p1)==True
            # then we need to substitute input parameter for the returned method and guard as well
            if m.inputs != trans[0].method.inputs:
                m = substitute_inputs(trans[0].method, m)
            else:
                m.guard = trans[0].method.guard
            o = ra.Observer(method=m, output=automaton.OUTPUTS[v])
            o.literal = automaton.LITERALS[o]

        observers.append(o)
    return observers


def get_contracts(config_, location_, wp_):
    global automaton, location, wp
    automaton = config_
    location = location_
    wp = wp_

    logging.debug('\n')
    logging.debug('Generating contract at location: ' + str(location))
    logging.debug('Observer method at post-state: ' + str(wp))
    logging.debug('Derived weakest precondition:' + str(wp.method.guard))

    # initialize the list of contracts
    contracts = list()

    # first gather guard conditions for each of the symbols at this location
    # second ask z3 for minimal unsatisfiable subsets
    # filter the subsets according to required constraints over subsets
    # create contracts
    # return contracts

    observ = observers()
    conditions = get_conditions(observ)

    if str(wp.method.guard) in ['True', 'False']:
        contracts = crate_contracts(observers=observ)
    else:
        logging.debug('Candidate observer methods at pre-state: ' + str(observ))
        logging.debug('Guards for the candidates: ' + str(conditions))
        subsets = get_MUSes(conditions)
        # check_subset(subsets)
        logging.debug('\n')
        logging.debug('MUSes after excluding WP:')
        [logging.debug(str(s)) for s in subsets]
        contracts = crate_contracts(observ, subsets)

    return contracts
