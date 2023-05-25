import logging

from errors import *

import constraintsolver.solver as SOLVER
from constraintsolver.blalgebra import simplify

automaton = None


def simplify_cond(contracts):
    print('\n\n ================ FINAL CONTRACTS AFTER SIMPLIFICATION ====================')
    logging.info('\n\n ================ FINAL CONTRACTS AFTER SIMPLIFICATION ====================')
    for contract in contracts:
        pre = contract.pre
        post = contract.post
        preexpr = SOLVER.z3reftoStr(pre.expression)
        postexpr = SOLVER.z3reftoStr(post.expression)
        # logging.debug('Simplify the following:')
        # logging.debug('Precondition: ' + preexpr)
        # logging.debug('Postcondition: ' + postexpr)
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
                logging.debug('Contract 1 Exp: ' + SOLVER.z3reftoStr(contract1.pre.expression) + ' ' + SOLVER.z3reftoStr(
                    contract1.post.expression))
                logging.debug('Contract 2: ' + str(contract2))
                logging.debug('Contract 2 Exp: ' + SOLVER.z3reftoStr(contract2.pre.expression) + ' ' + SOLVER.z3reftoStr(
                    contract1.post.expression))
                contract1 = contract1 & contract2
                logging.debug('New contract: ' + str(contract1))
                logging.debug('New Exp: ' + SOLVER.z3reftoStr(contract1.pre.expression) + ' ' + SOLVER.z3reftoStr(
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


def synthesize(config):
    global automaton
    automaton = config
    logging.debug('\n\nObserver to Boolean literal mapping:')
    for key in config.LITERALS:
        logging.debug(str(key.method) + ' : ' + config.LITERALS[key])
    logging.debug('\n')

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
