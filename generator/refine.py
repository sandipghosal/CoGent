import logging

import constraintsolver.solver as S

contracts = None


def check_post(first, second):
    # check if first.post and second.pre => second.post
    vars = list(set(first.variables) | set(second.variables))
    first_post = S.do_substitute(first.post.guard, first.constants)
    second_pre = S.do_substitute(second.pre.condition, second.constants)
    second_post = S.do_substitute(second.post.guard, second.constants)
    if S.check_sat(vars, S._and(first_post,second_pre), second_post) == S._sat():
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


def check_subsumption(first):
    for second in contracts:
        if first != second:
            logging.debug('Checking IF the contract:')
            logging.debug(first)
            logging.debug('subsumes the following:')
            logging.debug(second)

            # if both are true remove the second contract
            if check_pre(first, second) and check_post(first, second):
                logging.debug('Result: True')
                logging.debug('Removing the contract:')
                logging.debug(second)
                contracts.remove(second)
                logging.debug('\n')
            else:
                logging.debug('Result: False\n')



def refine(contracts_):
    global contracts
    contracts = contracts_
    logging.debug('\n\nStarting Contract Refinement')
    for contract in contracts:
        check_subsumption(contract)

    logging.debug('\n\n============= CONTRACTS AFTER REFINEMENT ===========')
    for item in contracts:
        logging.debug(item)
    logging.debug('\n')
    return contracts
