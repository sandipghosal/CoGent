import copy
import logging
from pprint import pp
import constraintbuilder
import constraintsolver.solver as S
from conditionbuilder.condition import Condition
from ramodel import Method
from ramodel.config import Monomial

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

        # # following checks are performed for the postconditions
        # for monomial in self.post.monomials:
        #     # first check if each monomial from self exists in other
        #     assert monomial in other.post.monomials
        #     i = other.post.monomials.index(monomial)
        #     for observer in monomial.observers:
        #         # check each observer of each monomial also exists in other monomial
        #         assert observer in other.post.monomials[i].observers
        #         j = other.post.monomials[i].observers.index(observer)
        #         # output of the observers should be the same
        #         if observer.output != other.post.monomials[i].observers[j].output:
        #             return False
        # return True

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
        self.post = self.post | other.post
        inputs = set()
        for monomial in self.pre.monomials:
            for observer in monomial.observers:
                {inputs.add(x) for x in observer.method.inputs}
        inputs = list(inputs)
        if len(inputs) == 1:
            self.target.inputs = inputs
        else:
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
        inputs = set()
        for monomial in self.pre.monomials:
            for observer in monomial.observers:
                {inputs.add(x) for x in observer.method.inputs}
        inputs = list(inputs)
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
                    first.method.guard = S.do_substitute(first.method.guard, monomial.substitutes)
                    first.method.inputs = [S.z3reftoStr(monomial.substitutes[0][1])]
                    flag = True

                    # hard code hack for the time being
                    automaton.LITERALS[first] = 'a0'

                    for second in monomial.observers:
                        if second.method.name.find('__equality__') != -1 or id(first) == id(second):
                            continue
                        if first.method == second.method and first.method.guard == S.do_substitute(second.method.guard,
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
            constants.append((S._int(c), S._intval(k)))

        # gather all the registers and parameters
        for monomial in self.pre.monomials:
            for observer in monomial.observers:
                for x in observer.method.inputs:
                    params.add(S._int(x))

        for r in (*automaton.REGISTERS, *automaton.TARGET.inputs):
            params.add(S._int(r))

        # Substitute constants with respective values
        pre = S.do_substitute(self.pre.condition, constants)
        post = S.do_substitute(self.post.condition, constants)

        logging.debug('Checking SAT for: ' + str(pre) + ' => ' + str(post))

        # Check the validity
        result = S.check_sat(vars=list(params), antecedent=pre, consequent=post)

        logging.debug('result: ' + str(result) + '\n')

        if result == S._sat():
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
                substitute.append((S._int(item), S._int(other)))
    # observer.method.guard = S.do_substitute(observer.method.guard, substitute)
    # observer.method.inputs = [S.z3reftoStr(substitute[0][1])]
    return substitute


def update_method_param(contract):
    """
    Update target method parameter when equality has been enforced in a monomial
    Example: push(p1) should become push(b0) when (p1==b0) is enforced
    :param contract:
    :return:
    """
    substitutes = contract.pre.monomials[0].substitutes
    for i in range(len(substitutes)):
        for j in range(len(contract.target.inputs)):
            param = S.z3reftoStr(substitutes[i][0])
            if contract.target.inputs[j] == param:
                contract.target.inputs[j] = S.z3reftoStr(substitutes[i][1])

def create_contract(monomial_):
    observers = copy.deepcopy(monomial_.observers)
    submonomial = list()
    condition = None
    last_contract = None

    for i in range(len(observers)):
        if observers[i].method.name.find('__equality__') != -1 \
                and observers[i].output == automaton.OUTPUTS['TRUE']:
            [monomial_.substitutes.append(x) for x in get_substitutes(observers[i])]
        elif observers[i].method.name.find('__equality__') != -1 \
                and observers[i].output == automaton.OUTPUTS['FALSE']:
            pass
        else:
            # for an observer method obtain the transition due to the method
            transition = location.get_transitions(destination=location, method=observers[i].method,
                                                  output=observers[i].output)
            # if there is no transition found continue the iteration
            if not transition:
                continue

            if observers[i].method.inputs:
                # build the list of tuple to substitute method's parameter with the observer's parameter
                _args = [(S._int(transition[0].method.inputs[0]), S._int(observers[i].method.inputs[0]))]
                # get the method condition by substituting
                observers[i].method.guard = S.do_substitute(transition[0].method.guard, _args)
            else:
                observers[i].method.guard = transition[0].method.guard
            # observers[i].method.guard = transition[0].method.guard

        submonomial.append(observers[i])

        if condition is not None:
            # do the conjunction for more than one observers
            condition = S._and(condition, observers[i].method.guard)
        else:
            condition = observers[i].method.guard

        # create precondition with the monomial subset
        premonomial = Monomial(submonomial, condition=condition, substitute=monomial_.substitutes)
        pre = Condition([premonomial], automaton)

        # create postcondition with the wp
        postmonomial = Monomial([wp], condition=wp.method.guard)
        post = Condition([postmonomial], automaton)

        # create a copy of the target method
        target = copy.deepcopy(automaton.TARGET)

        logging.debug('Location: ' + str(location))
        logging.debug('Postcondition: ' + str(post))
        logging.debug('Weakest Precondition (consequent): ' + str(post.condition))
        logging.debug('Precondition: ' + str(pre))
        logging.debug('Precondition (antecedent): ' + str(pre.condition))

        # create a Contract and store into last_contract
        last_contract = Contract(pre, target, post)

        if not last_contract.result:
            # if any part of the result is unsat abort the building process
            # and return None
            logging.debug('Precondition is inconsistent\n')
            for observer in submonomial:
                if observer.method.name.find('__equality__') == -1:
                    # make sure at least one non-equality observer is present in the monomial
                    # then return the last obtained consistent contract
                    return last_contract
        else:
            logging.debug('Precondition is consistent\n')
            if last_contract.apply_equalities():
                update_method_param(last_contract)
                last_contract.pre.mapping = last_contract.pre.build_map(automaton.LITERALS)
                last_contract.pre.expression = last_contract.pre.get_expression(automaton)
                last_contract.pre.expr_text = last_contract.pre.get_text(last_contract.pre.mapping)

    return last_contract



            # for i in range(len(monomial_.substitutes)):
            #     for j in range(len(target.inputs)):
            #         param = S.z3reftoStr(monomial_.substitutes[i][0])
            #         if target.inputs[j] == param:
            #             target.inputs[j] = S.z3reftoStr(monomial_.substitutes[i][1])




def get_contracts(config_, location_, wp_):
    global automaton, location, wp
    automaton = config_
    location = location_
    wp = wp_

    # initialize the list of contracts
    contracts = list()

    for monomial in automaton.MONOMIALS:
        logging.debug('\n')
        logging.debug('Generate contract for the monomial: ' + str(monomial))
        contract = create_contract(monomial)
        if contract is None:
            continue
        if contract.result:
            logging.debug(contract)
            contracts.append(contract)
    return contracts
