import logging

import constraintsolver.solver as S

automaton = None


def check_post(first, second):
    # check if first.post and second.pre => second.post
    vars = list(set(first.variables) | set(second.variables))
    first_post = S.do_substitute(first.post.guard, first.constants)
    second_pre = S.do_substitute(second.pre.condition, second.constants)
    second_post = S.do_substitute(second.post.guard, second.constants)
    if S.check_sat(vars, S._and(first_post, second_pre), second_post) == S._sat():
        return False
    else:
        return True


def check_pre(first, second):
    # check if second.pre => first.pre
    params = set()
    constants = list()
    # gather the constants for substitution
    for c, k in automaton.CONSTANTS:
        constants.append((S._int(c), S._intval(k)))

    # gather all the registers and parameters
    for observer in list(set(first.monomial.observers) | set(second.monomial.observers)):
        for x in observer.method.inputs:
            params.add(S._int(x))

    first_pre = S.do_substitute(first.monomial.condition, constants)
    second_pre = S.do_substitute(second.monomial.condition, constants)
    if S.check_sat(list(params), second_pre, first_pre) == S._sat():
        return False
    else:
        return True


def subsumes(first, second):
    logging.debug('Checking IF the contract:')
    logging.debug(first)
    logging.debug('subsumes the following:')
    logging.debug(second)

    return True if check_pre(first, second) else False

    # uncomment the following if use refinement definition
    # if both are true remove the second contract
    # if check_pre(first, second) and check_post(first, second):
    #     return True
    # else:
    #     return False


def check_subsumption():
    for location in automaton.LOCATIONS.values():
        temp = list()

        # for i in range(len(contracts)-1, -1, -1):
        for first in location.contracts:
            # due to transitivity property if a contract is checked
            # to be subsumed by another (hence in the list temp)
            # we do not need to investigate that contract further
            if first in temp:
                continue
            for second in location.contracts:
                if id(first) == id(second):
                    # if first and second referring to same contract object
                    continue
                # do subsumption check only if two contracts are not same but their post-conditions are same
                if first.wp == second.wp:
                    if subsumes(first, second):
                        logging.debug('Result: True')
                        logging.debug('Adding the following into the list of possible abandoned contracts:')
                        temp.append(second)
                        logging.debug(second)
                        logging.debug('\n')
                    else:
                        logging.debug('Result: False\n')
        location.contracts[:] = [item for item in location.contracts if item not in temp]

    automaton.print_contracts('============= CONTRACTS AFTER REFINEMENT ===========')


def remove_duplicates():
    for location in automaton.LOCATIONS.values():
        for contract1 in location.contracts[:]:
            for contract2 in location.contracts[:]:
                if id(contract1) != id(contract2) and contract1 == contract2:
                    location.contracts.remove(contract2)

    automaton.print_contracts('============= CONTRACTS AFTER REMOVING DUPLICATES ===========')


def remove_inconsistency():
    temp_list = set()
    logging.debug('Inconsistent contracts:')
    for location in automaton.LOCATIONS.values():
        for first in location.contracts:
            if first in temp_list:
                continue
            flag = False
            logging.debug('\n')
            for second in location.contracts:
                if id(first) != id(second) and (first.monomial == second.monomial):
                    if flag:
                        temp_list.add(second)
                        logging.debug(second)
                    if first.post.output != second.post.output:
                        flag = True
                        logging.debug(first)
                        logging.debug(second)
                        temp_list.add(first)
                        temp_list.add(second)

        location.contracts[:] = [item for item in location.contracts if item not in temp_list]

    automaton.print_contract('============= CONTRACTS AFTER REMOVING INCONSISTENCIES ===========')


def refine(config):
    global automaton
    automaton = config
    logging.debug('\n====================== Starting Contract Refinement ==========================')
    # remove_inconsistency()
    remove_duplicates()
    check_subsumption()
