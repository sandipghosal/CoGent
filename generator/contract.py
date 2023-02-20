import copy
import logging
from pprint import pp
import constraintbuilder
import constraintsolver.solver as S
from ramodel import Method
from ramodel.config import Monomial

automaton = None
location = None
wp = None


class Contract:
    def __init__(self, monomial, target, observer, result=None):
        """
        Hold a contract for a location
        :param monomial: Object of Monomial class that serves the precondition
        :param observer: Object of Observer class that serves the postcondition
        :param result: Result True/False representing a valid or invalid contract
        """

        self.monomial = monomial
        self.target = target
        self.wp = observer
        if result is not None:
            self.result = result
        else:
            self.result = self.check()

        # self.result = self.check(params, registers, constants)
        # obtain precondition from the observers
        # check of precondition => weakestpre is satisfied and store into self.result

    def __eq__(self, other):
        return self.monomial == other.monomial and self.wp == other.wp and self.wp.output == other.wp.output and self.result == other.result

    def __hash__(self):
        return hash(str(self.monomial) + str(self.wp))

    def __repr__(self):
        return '{' + str(self.monomial) + '} ' + str(self.target) + ' {' + str(self.wp) + '} :: ' + str(self.result)

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
        for observer in self.monomial.observers:
            for x in observer.method.inputs:
                params.add(S._int(x))

        for r in (*automaton.REGISTERS, *automaton.TARGET.inputs):
            params.add(S._int(r))

        # Substitute constants with respective values
        pre = S.do_substitute(self.monomial.condition, constants)
        post = S.do_substitute(self.wp.method.guard, constants)

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


def apply_equalities(submonomial):
    substitute = list()
    logging.debug('Check for equalities')
    for observer in submonomial:
        if observer.method.name.find('__equality__') != -1 and observer.output == automaton.OUTPUTS['TRUE']:
            substitute.append((S._int(observer.method.inputs[0]), S._int(observer.method.inputs[1])))
    if not substitute:
        logging.debug('No equality found')
        return submonomial

    for first in submonomial:
        for second in submonomial:
            if second.method.name.find('__equality__') != -1 or id(first) == id(second):
                continue
            if first.method == second.method and first.method.guard == S.do_substitute(second.method.guard, substitute):
                logging.debug(str(first) + ' == ' + str(second))
                logging.debug('Removing observer: ' + str(second))
                submonomial.remove(second)
    return submonomial


def create_contract(monomial_):
    observers = copy.deepcopy(monomial_.observers)
    result = None
    last_contract = None
    submonomial = list()
    for i in range(len(observers)):
        # iterate for each observer in the monomial
        if observers[i].method.name.find('__equality__') != -1:
            # if the observer is an equality build the equality expression based on the expected output
            if observers[i].output == automaton.OUTPUTS['TRUE']:
                observers[i].method.guard = constraintbuilder.build_expr(
                    observers[i].method.inputs[0] + '==' + observers[i].method.inputs[1])
            else:
                observers[i].method.guard = constraintbuilder.build_expr(
                    observers[i].method.inputs[0] + '!=' + observers[i].method.inputs[1])
        else:
            # for an observer method obtain the transition due to the method
            transition = location.get_transitions(destination=location, method=observers[i].method,
                                                  output=observers[i].output)
            # if there is no transition found continue the iteration
            if not transition:
                continue

            if observers[i].method.inputs != []:
                # build the list of tuple to substitute method's parameter with the observer's parameter
                _args = [(S._int(transition[0].method.inputs[0]), S._int(observers[i].method.inputs[0]))]
                # get the method condition by substituting
                observers[i].method.guard = S.do_substitute(transition[0].method.guard, _args)
            else:
                observers[i].method.guard = transition[0].method.guard

        if result is not None:
            # do the conjunction for more than one observers
            result = S._and(result, observers[i].method.guard)
        else:
            result = observers[i].method.guard

        # add the subset of the monomial into the list
        submonomial.append(observers[i])

        logging.debug('Location: ' + str(location))
        logging.debug('Postcondition: ' + str(wp))
        logging.debug('Weakest Precondition (consequent): ' + str(wp.method.guard))
        logging.debug('Precondition: ' + str(submonomial))
        logging.debug('Precondition (antecedent): ' + str(result))

        submonomial = apply_equalities(submonomial)

        # create a monomial object with the subset
        mobj = Monomial(submonomial, result)

        target = copy.deepcopy(automaton.TARGET)

        # create contract with this submonomial
        last_contract = Contract(mobj, target, wp)

        if not last_contract.result:
            # if any part of the result is unsat abort the building process
            # and return None
            logging.debug('Precondition is inconsistent\n')
            for observer in submonomial:
                if observer.method.name.find('__equality__') == -1:
                    # make sure at least one non-equality observer is present in the monomial
                    # then last obtained consistent contract
                    return last_contract
        else:
            logging.debug('Precondition is consistent\n')
            last_contract = last_contract

        # # substitute the constants first
        # result = S.do_substitute(result, constants)
        #
        # # gather all the registers and parameters
        # for p in (*observers[i].method.inputs, *automaton.REGISTERS, *automaton.TARGET.inputs):
        #     params.add(S._int(p))
        #
        # logging.debug('Precondition expression (antecedent): ' + str(result))

    return last_contract


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
