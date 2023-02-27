import copy
import logging

import constraintsolver.solver as S

automaton = None


def reformat():
    """
    Substitute condition of equalities such as (a==b) to (b==b) or True
    """
    for location in automaton.LOCATIONS.values():
        for contract in location.contracts:
            # if len(contract.monomial.observers) != 1:
            #     continue
            substitute = list()
            for observer in contract.monomial.observers:
                if observer.method.name.find('__equality__') != -1 and observer.output == automaton.OUTPUTS['TRUE']:
                    for item in (contract.target.inputs or contract.target.outputs):
                        for i in range(len(observer.method.inputs)):
                            if i == 0:
                                other = observer.method.inputs[i + 1]
                            else:
                                other = observer.method.inputs[i - 1]

                            if item == observer.method.inputs[i]:
                                substitute.append((S._int(item), S._int(other)))

                    observer.method.guard = S.do_substitute(observer.method.guard, substitute)
                    observer.method.inputs = [S.z3reftoStr(substitute[0][1])]

                    # a hard code hack for the time being
                    # insert an observer with only b0 into dict of LITERALS and map to a0
                    automaton.LITERALS[observer] = 'a0'


                if substitute != [] and observer.method.inputs:
                    for i in range(len(substitute)):
                        for j in range(len(observer.method.inputs)):
                            param = S.z3reftoStr(substitute[i][0])
                            if observer.method.inputs[j] == param:
                                observer.method.inputs[j] = S.z3reftoStr(substitute[i][1])

            if substitute != [] and contract.target.inputs:
                for i in range(len(substitute)):
                    for j in range(len(contract.target.inputs)):
                        param = S.z3reftoStr(substitute[i][0])
                        if contract.target.inputs[j] == param:
                            contract.target.inputs[j] = S.z3reftoStr(substitute[i][1])


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

    for reg in automaton.REGISTERS:
        params.add(S._int(reg))

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
        location.contracts.sort(key=lambda x: len(x.monomial))
        for i in range(len(location.contracts)):
            first = location.contracts[i]
            # due to transitivity property if a contract is checked
            # to be subsumed by another (hence in the list temp)
            # we do not need to investigate that contract further
            if first in temp:
                continue
            for j in range(len(location.contracts)):
                second = location.contracts[j]
                if id(first) == id(second):
                    # if first and second referring to same contract object
                    continue
                # do subsumption check only if two contracts are not same but their post-conditions are same
                if first.wp == second.wp and first.wp.output == second.wp.output and first.monomial.subset(
                        second.monomial):
                # if first.wp == second.wp and first.wp.output == second.wp.output:
                    logging.debug('Location: ' + str(location))
                    # if first.wp == second.wp and first.wp.output == second.wp.output:
                    if subsumes(first, second):
                        logging.debug('Result: True')
                        logging.debug('Adding the following into the list of abandoned contracts:')
                        temp.append(second)
                        logging.debug(second)
                        logging.debug('\n')
                    else:
                        logging.debug('Result: False\n')
        location.contracts[:] = [item for item in location.contracts if item not in temp]


def remove_duplicates():
    for location in automaton.LOCATIONS.values():
        location.contracts = list(dict.fromkeys(location.contracts))


def refine(config):
    global automaton
    automaton = config
    logging.debug('\n====================== Starting Contract Refinement ==========================')
    # remove_inconsistency()
    remove_duplicates()
    automaton.print_contracts('============= CONTRACTS AFTER REMOVING DUPLICATES ===========')
    check_subsumption()
    reformat()
    automaton.print_contracts('============= CONTRACTS AFTER REFINEMENT ===========')
