import copy
from errors import *

import constraintsolver.solver as S
import ramodel.config as CONFIG
from conditionbuilder import condition
from generator.contract import Contract

automaton = None


def meet_per_location(location):
    if not location.contracts:
        return
    logging.info('Contract for location :%s', location)
    for contract1 in location.contracts:
        for contract2 in location.contracts:
            if id(contract1) != id(contract2) and contract1.post == contract2.post:
                logging.debug('Meet of the following two contracts:')
                logging.debug('Contract 1: ' + str(contract1))
                logging.debug('Contract 1 Exp: ' + S.z3reftoStr(contract1.pre.expression) + ' ' + S.z3reftoStr(
                    contract1.post.expression))
                logging.debug('Contract 2: ' + str(contract2))
                logging.debug('Contract 2 Exp: ' + S.z3reftoStr(contract2.pre.expression) + ' ' + S.z3reftoStr(
                    contract1.post.expression))
                contract1 = contract1 & contract2
                logging.debug('New contract: ' + str(contract1))
                logging.debug('New Exp: ' + S.z3reftoStr(contract1.pre.expression) + ' ' + S.z3reftoStr(
                    contract1.post.expression))
                location.contracts.remove(contract2)
        logging.info(contract1)
        logging.info('\n')


def join_contracts(post):
    result = None
    for loc in automaton.LOCATIONS.values():
        for contract in loc.get_contracts(post=post):
            if not result:
                result = contract
            else:
                result = result | contract
    return result


def append(contract, observers):
    conjunct = None
    for observer in observers:
        if conjunct is None:
            conjunct = observer.method.guard
        else:
            conjunct = S._and(conjunct, observer.method.guard)

    monomial = CONFIG.Monomial(observers=observers, condition=conjunct)
    pre = condition.Condition([monomial], automaton)
    post = copy.copy(contract.post)
    newcontract = Contract(pre, contract.target, post, True)
    contract.pre = newcontract.pre.implies(contract.pre)
    return contract


def padding(location):
    """
    pad STATE_SYMBOLS with each contract if the location
    :param location:
    :return:
    """
    # for each observer in STATE_SYMBOL
    # get the transition wrt. the symbol
    # prepare the observer method
    # for each contract in location
    # append the precondition with the observer method
    observers = list()
    for x in automaton.STATE_SYMBOLS:
        transitions = location.get_transitions(destination=location, method=x, output=automaton.OUTPUTS['TRUE'])
        if not transitions:
            transitions = location.get_transitions(destination=location, method=x, output=automaton.OUTPUTS['FALSE'])
        assert len(transitions) == 1
        observer = copy.deepcopy(automaton.OBSERVERS[transitions[0].method.name])
        observer.method = transitions[0].method
        observer.output = transitions[0].output
        observer.literal = automaton.LITERALS[observer]
        observers.append(observer)

    for contract in location.contracts:
        contract = append(contract, observers)


def synthesize(config):
    global automaton
    automaton = config
    logging.debug('\n\nObserver to Boolean literal mapping:')
    logging.debug(config.LITERALS)

    for location in automaton.LOCATIONS.values():
        meet_per_location(location)
        if automaton.STATE_SYMBOLS and location.contracts:
            padding(location)
    automaton.print_contracts('================ CONTRACTS PER LOCATION ====================')

    logging.info('\n\n===================== FINAL CONTRACT =====================')
    print('\n\n===================== FINAL CONTRACT =====================')
    posts = set()
    for location in automaton.LOCATIONS.values():
        for contract in location.contracts:
            posts.add(contract.post)
    for x in posts:
        final = join_contracts(x)
        logging.info(final)
        print(final)
