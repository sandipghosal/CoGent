import copy

from errors import *

import constraintsolver.solver as S
import ramodel.config as CONFIG
from conditionbuilder import condition
from generator.contract import Contract
from constraintsolver.blalgebra import simplify

automaton = None


def simplify_cond(contracts):
    print('\n\n ================ FINAL CONTRACTS ====================')
    logging.info('\n\n ================ FINAL CONTRACTS ====================')
    for contract in contracts:
        pre = contract.pre
        post = contract.post
        preexpr = S.z3reftoStr(pre.expression)
        postexpr = S.z3reftoStr(post.expression)
        pre.expr_text = pre.get_text(pre.mapping, simplify(preexpr))
        post.expr_text = post.get_text(post.mapping, simplify(postexpr))
        contract.pre = pre
        contract.post = post
        if contract.pre.expr_text != 'False':
            logging.info(str(contract))
            print(str(contract))


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


# the following join function does consider all locations including first and last
def join_contracts(post):
    result = None
    for loc in automaton.LOCATIONS.values():
        for contract in loc.get_contracts(post=post):
            if not result:
                result = contract
            else:
                result = result | contract
    return result


# the following join function does not consider first and last location of the automaton
# def join_contracts(post):
#     result = None
#     locations = list(automaton.LOCATIONS.values())
#     for i in range(len(locations)):
#         if i !=0 and i < len(locations)-1:
#             for contract in locations[i].get_contracts(post=post):
#                 if not result:
#                     result = contract
#                 else:
#                     result = result | contract
#     return result


def add_dummy_contract(location):
    """
    add dummy contract for isfull() or isempty() whichever does not exist in the contract list
    :param location: object of Location
    :return:
    """
    destinations = location.get_destinations(method=automaton.TARGET)
    for symbol in automaton.STATE_SYMBOLS:
        observer = None
        for dest in destinations:
            # if the observer with output True does exist
            # in any of the destinations then abort and move on to next symbol
            observer = create_observer(dest, symbol, automaton.OUTPUTS['True'])
            if observer:
                break
        # cannot create an observer if there is no such transition
        # if there is no such observer we can create a dummy contract with precondition 'False'
        if observer:
            continue


def append(contract, observers):
    conjunct = None
    for observer in observers:
        if conjunct is None:
            conjunct = observer.method.guard
        else:
            conjunct = S._and(conjunct, observer.method.guard)

    monomial = CONFIG.Monomial(observers=observers, condition=conjunct)
    pre = condition.Condition([monomial], automaton)
    post = copy.deepcopy(contract.post)
    newcontract = Contract(pre, contract.target, post, True)
    # Do implication: appended observers => contract
    contract.pre = newcontract.pre.implies(contract.pre)
    # Do conjunction: appended observers and contract
    # contract = contract | newcontract
    return contract


def create_observer(location, method, output):
    """
    Create an object of Observer for a given location, method, and output
    :param location: Object of Location
    :param method: Object of Method
    :param output: Object of Output
    :return: Object of Observer or None
    """
    transitions = location.get_transitions(destination=location, method=method, output=output)
    if not transitions:
        return None
    assert len(transitions) == 1
    observer = copy.deepcopy(automaton.OBSERVERS[transitions[0].method.name])
    observer.method = transitions[0].method
    observer.output = transitions[0].output
    observer.literal = automaton.LITERALS[observer]
    return observer


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
        observer = create_observer(location, x, automaton.OUTPUTS['TRUE'])
        if observer is None:
            observer = create_observer(location, x, automaton.OUTPUTS['FALSE'])
        observers.append(observer)
    if not observers:
        return
    for contract in location.contracts:
        contract = append(contract, observers)


def synthesize(config):
    global automaton
    automaton = config
    logging.debug('\n\nObserver to Boolean literal mapping:')
    for key in config.LITERALS:
        logging.debug(str(key.method) + ' : ' + config.LITERALS[key])
    logging.debug('\n')

    locations = list(automaton.LOCATIONS.values())
    for i in range(len(locations)):
        # add_dummy_contract(locations[i])
        meet_per_location(locations[i])
        if automaton.STATE_SYMBOLS and locations[i].contracts:
            padding(locations[i])
            # append isfull and isempty only for first and last locations
            # if i == 0 or i == len(locations) - 1:
            #     padding(locations[i])

    automaton.print_contracts('================ CONTRACTS PER LOCATION ====================')

    logging.debug('\n\n===================== LOCATION INDEPENDENT CONTRACTS =====================')
    posts = set()

    for location in automaton.LOCATIONS.values():
        for contract in location.contracts:
            posts.add(contract.post)
    # store the list of contracts after joining across the locations
    contracts = list()
    for x in posts:
        final = join_contracts(x)
        logging.debug(final)
        contracts.append(final)

    # simplify contracts using the library sympy
    simplify_cond(contracts)
