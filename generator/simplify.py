import logging

from errors import *

import constraintsolver.solver as SOLVER
from constraintsolver.blalgebra import simplify
import generator.contract as CONTRACT

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


def prune(post):
    """
    Prune the list of contracts obtained across different locations by checking subsumptions
    :param posts: set of postconditions (Condition object)
    """

    logging.debug('\nList of contracts across the locations for postcondition %s', str(post))
    old = list()
    new = list()
    cnts = list()
    for l in automaton.LOCATIONS.values():
        for c in l.get_contracts(post=post):
            logging.debug(c)
            # collect contracts with precondition other than "True" in a separate list
            if str(c.pre.condition) != "True":
                cnts.append(c)
            else:
                new.append(c)
    old = list(cnts)
    [new.append(c) for c in CONTRACT.check_subsumption(cnts)]
    return new





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


    posts = set()

    for location in automaton.LOCATIONS.values():
        for contract in location.contracts:
            posts.add(contract.post)
    # check subsumption for the contracts obtained in each location wrt. each postcondition

    logging.debug('\n\n===================== LOCATION INDEPENDENT CONTRACTS =====================')
    # store the list of contracts after joining across the locations
    contracts = list()
    for x in posts:
        # prune(x)
        final = join_contracts(x)
        logging.debug(final)
        contracts.append(final)

    # simplify contracts using the library sympy
    simplify_cond(contracts)
