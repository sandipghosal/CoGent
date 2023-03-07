import copy
import itertools
import logging
from errors import *

import constraintsolver.solver as S
from constraintbuilder import build_str

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


def append(location, observers):
    for contract in location.contracts:
        for observer in observers:
            contract.monomial.observers.append(observer)


def padding(location, methods):
    transitions = location.get_transitions(location)
    if transitions == []:
        return
    observers = list()
    for method in methods:
        for transition in transitions:
            if transition.method == method:
                observer = copy.deepcopy(automaton.OBSERVERS[transition.method.name])
                observer.method = transition.method
                observer.output = transition.output
                observer.literal = automaton.LITERALS[observer]
                observers.append(observer)
    if observers == []:
        return
    append(location, observers)


def methods_for_padding():
    methods = list()
    for observer in automaton.OBSERVERS.values():
        methods.append(observer.method)
    for location in automaton.LOCATIONS.values():
        for contract in location.contracts:
            for observer in contract.monomial.observers:
                if observer.method.name.find('__equality__') != -1:
                    continue
                if observer.method in methods and S.z3reftoStr(observer.method.guard) != 'True':
                    methods.remove(observer.method)
    return methods


def synthesize(config):
    global automaton
    automaton = config
    logging.debug('\n\nObserver to Boolean literal mapping:')
    logging.debug(config.LITERALS)

    for location in automaton.LOCATIONS.values():
        meet_per_location(location)
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
