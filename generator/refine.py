import logging

import constraintsolver.solver as S

contracts = None


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
    vars = list(set(first.variables) | set(second.variables))
    first_pre = S.do_substitute(first.pre.condition, first.constants)
    second_pre = S.do_substitute(second.pre.condition, second.constants)
    if S.check_sat(vars, second_pre, first_pre) == S._sat():
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
    temp = list()
    # for i in range(len(contracts)-1, -1, -1):
    for first in contracts:
        # due to transitivity property if a contract is checked
        # to be subsumed by another (hence in the list temp)
        # we do not need to investigate that contract further
        if first in temp:
            continue
        for second in contracts:
            if id(first) == id(second):
                # if first and second referring to same contract object
                continue
            # do subsumption check only if two contracts are not same but their post-conditions are same
            if first.post == second.post:
                if subsumes(first, second):
                    logging.debug('Result: True')
                    logging.debug('Adding the following into the list of possible abandoned contracts:')
                    temp.append(second)
                    logging.debug(second)
                    logging.debug('\n')
                else:
                    logging.debug('Result: False\n')
    contracts[:] = [item for item in contracts if item not in temp]


def remove_duplicates():
    global contracts
    contracts = list(set(contracts))
    logging.debug('\n\n============= CONTRACTS AFTER REMOVING DUPLICATES ===========')
    for item in contracts:
        logging.debug(item)
    logging.debug('\n')


def remove_inconsistency():
    temp_list = set()
    logging.debug('Inconsistent contracts:')
    for first in contracts:
        if first in temp_list:
            continue
        flag = False
        logging.debug('\n')
        for second in contracts:
            if id(first) != id(second) and (first.pre == second.pre):
                if flag:
                    temp_list.add(second)
                    logging.debug(second)
                if first.post.output != second.post.output:
                    flag = True
                    logging.debug(first)
                    logging.debug(second)
                    temp_list.add(first)
                    temp_list.add(second)

    contracts[:] = [item for item in contracts if item not in temp_list]
    logging.debug('\n\n============= CONTRACTS AFTER REMOVING INCONSISTENCIES ===========')
    for item in contracts:
        logging.debug(item)
    logging.debug('\n')


def refine(contracts_):
    global contracts
    contracts = contracts_
    logging.debug('\n\nStarting Contract Refinement')
    remove_inconsistency()
    remove_duplicates()
    check_subsumption()

    logging.debug('\n\n============= CONTRACTS AFTER REFINEMENT ===========')
    for item in contracts:
        logging.debug(item)
    logging.debug('\n')
    return contracts
