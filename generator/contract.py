import copy
import itertools
import logging

import smtsolvers.solver as SOLVER
import smtsolvers.MUS as MUS
import smtsolvers.blalgebra as SIMPLIFIER
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

    def subsumes(self, other):
        """
        Does first contract subsume other contract
        :param other: Contract Object
        :return: True or False
        """
        if self == other:
            return True
        else:
            return subsumes(self, other)


# def add_invariants(contracts, invariants):
#     """
#     If invariants is I = [a1, a2], then contract generated as {(a1 v a2) -> c} f {b1}
#     :param contracts:
#     :param invariants:
#     :return:
#     """
#     pre = None
#     for i in invariants:
#         m = Monomial(observers=[i], condition=i.method.guard)
#         if not pre:
#             pre = Condition([m], automaton)
#         else:
#             cond = Condition([m], automaton)
#             pre = pre | cond
#
#     assert str(pre.condition) == 'True'
#
#     for con in contracts:
#         new = Contract(copy.deepcopy(pre), con.target, con.post, True)
#         # Do implication: appended observers => contract
#         con.pre = new.pre.implies(con.pre)
#     return contracts


def add_invariants(contracts, invariants):
    """
    If invariants is I = [a1, a2], then contract generated as {a1^a2 -> c} f {b1}
    (deafult behaviour)
    :param contracts:
    :param invariants:
    :return:
    """
    for con in contracts:
        m = Monomial(observers=invariants, condition=SOLVER._boolval(True))
        pre = Condition([m], automaton)
        new = Contract(pre, con.target, con.post, True)
        # Do implication: appended observers => contract
        con.pre = new.pre.implies(con.pre)
    return contracts


def join_contracts(contracts):
    assert len(contracts) > 1

    pre = None
    c = None
    for c in contracts:
        if not pre:
            pre = c.pre
        else:
            pre = pre | c.pre
    new = Contract(pre, c.target, c.post, True)
    return [new]


def check_pre(first, second):
    # check if second.pre => first.pre
    params = set()
    constants = list()
    # gather the constants for substitution
    for c, k in automaton.CONSTANTS:
        constants.append((SOLVER._int(c), SOLVER._intval(k)))

    # gather all the registers and parameters
    for observer in list(set(first.pre.monomials[0].observers) | set(second.pre.monomials[0].observers)):
        # for observer in list(set(first.monomial.observers) | set(second.monomial.observers)):
        for x in observer.method.inputs:
            params.add(SOLVER._int(x))

    for reg in automaton.REGISTERS:
        params.add(SOLVER._int(reg))

    first_pre = SOLVER.do_substitute(first.pre.condition, constants)
    second_pre = SOLVER.do_substitute(second.pre.condition, constants)
    # first_pre = S.do_substitute(first.monomial.condition, constants)
    # second_pre = S.do_substitute(second.monomial.condition, constants)

    if SOLVER.check_sat(list(params), second_pre, first_pre) == SOLVER._sat():
        return False
    else:
        return True

def rank_contract(c):
    """
    Give the contract a rank based on no. of equalities,
    no. of parameters.
    :param c: a Contract object
    :return: int rank
    """
    rank = len(c.pre.monomials[0].observers)*5
    for o in c.pre.monomials[0].observers:
        if o.method.name in automaton.OBSERVERS.keys():
            for i in o.method.inputs:
                rank = rank + 1
    return rank


def subsumes(first, second):
    logging.debug('Checking IF the contract:')
    logging.debug(first)
    logging.debug('subsumes the following:')
    logging.debug(second)

    return True if check_pre(first, second) else False



def check_subsumption(contracts):
    if len(contracts) == 1:
        return contracts
    # list of contracts that are subsumed by others
    temp = list()
    contracts.sort(key=lambda x: rank_contract(x))
    for i in range(len(contracts)):
        f = contracts[i]
        # due to transitivity property if a contract is checked
        # to be subsumed by another (hence in the list temp)
        # we do not need to investigate that contract further
        if f in temp:
            continue
        for j in range(len(contracts)):
            s = contracts[j]
            if f == s:
                continue
            # do subsumption check only if two contracts are not same but their post-conditions are same
            assert f.post == s.post
            if subsumes(f, s):
                logging.debug('Result: True')
                logging.debug('Adding the following into the list of abandoned contracts:')
                temp.append(s)
                logging.debug(s)
                logging.debug('\n')
            else:
                logging.debug('Result: False\n')
    contracts[:] = [item for item in contracts if item not in temp]
    return contracts


def new_literal(monomial):
    for o in monomial.observers:
        if o in automaton.LITERALS.keys():
            o.literal = automaton.LITERALS[o]
        else:
            automaton.update_literals(copy.deepcopy(o), o.literal)


def update_monomials(monomials, subs):
    # initially there should be only one monomial in the list
    assert len(monomials) == 1
    for m in monomials:
        m.substitutes = subs
        m.do_substitute()
        m.update_params()
        # might need to assign new literal due to update
        new_literal(m)


def get_substitutes(contract):
    sub = list()
    # first check if there is at least one equality and non-parameterized observers
    # on the way collect input parameters for the equalities that are true
    oparams = set()
    for m in contract.pre.monomials:
        for o in m.observers:
            if o.method.name.find('__equality__') != -1 and o.output == automaton.OUTPUTS['TRUE']:
                for p in o.method.inputs:
                    oparams.add(p)
            elif o.method.name.find('__equality__') != -1 and o.output == automaton.OUTPUTS['FALSE']:
                return []
            elif not o.method.inputs:
                continue
            else:
                return []
    # collect the input parameters for target method
    tparams = automaton.TARGET.inputs

    # for each param in tparams if that exists in oparams then create tuples
    # example: tparams = [p1, p2] and oparams = [b0, p1]
    # since p1 is in oparams create tuples (b0, p1)
    # since p2 is not in oparams so no replacement for p2
    for q in tparams:
        if q in list(oparams):
            [sub.append((SOLVER._int(p), SOLVER._int(q))) for p in list(oparams) if p != q]
    return sub


def apply_equality(contracts):
    for c in contracts:
        subs = get_substitutes(c)
        if subs:
            update_monomials(c.pre.monomials, subs)
            c.pre.update(automaton)
            update_monomials(c.post.monomials, subs)
            c.post.update(automaton)
    return contracts


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
    logging.debug('Following contracts are generated from MUSes:')
    contracts = list()
    # if the set of constraint is blank then
    # we can just add a contract like {True} push(p1){wp}
    if not constraints or constraints == [[]]:
        if str(wp.method.guard) == 'False':
            # observer = create_observer('False', wp.method.guard)
            observer = create_observer('False', SOLVER._boolval(False))
        else:
            # observer = create_observer('True', wp.method.guard)
            observer = create_observer('False', SOLVER._boolval(True))

        pre = prepare_condition([observer])
        post = prepare_condition([copy.deepcopy(wp)])
        contract = Contract(pre, copy.deepcopy(automaton.TARGET), post, True)
        logging.debug(contract)
        contracts.append(contract)

    else:
        for c in constraints:
            pre = prepare_condition(observers, c)
            post = prepare_condition([copy.deepcopy(wp)])
            # create a contract
            contract = Contract(pre, copy.deepcopy(automaton.TARGET), post, True)
            logging.debug(contract)
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


def get_contracts(config_, location_, wp_, invariants):
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
    # check for subsumption
    contracts = check_subsumption(contracts)

    # do the inline substitution for contracts that
    # does not have parameterized method in the pre-condition
    # contracts = apply_equality(contracts)
    # join multiple contracts
    if len(contracts) > 1:
        contracts = join_contracts(contracts)
    # add location-specific invariants to each contract
    if invariants:
        contracts = add_invariants(contracts, invariants)
    return contracts
