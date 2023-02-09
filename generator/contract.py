import logging
from pprint import pp

import constraintsolver.solver as S
from ramodel import Method


class Contract:
    def __init__(self, target, location, params, registers, constants, precondition, postcondition):
        """
        Hold a contract for a modifier in the form of precondition and postcondition
        :param target: target Method object
        :param location: an object of Location
        :param params: input parameters of target methods and observers
        :param registers: list of registers
        :param constants: list of constants [(id, value),..]
        :param precondition: an object of Precondition
        :param postcondition: object of Postcondition
        """
        self.target = target
        self.location = location
        self.pre = precondition
        self.post = postcondition
        self.variables = params + registers
        self.constants = constants
        if self.check() == S._sat():
            self.result = False
        else:
            self.result = True
        # self.result = self.check(params, registers, constants)
        # obtain precondition from the observers
        # check of precondition => weakestpre is satisfied and store into self.result

    def __eq__(self, other):
        return self.pre == other.pre and self.post == other.post

    def __hash__(self):
        return hash(str(self.pre) + str(self.post))

    def __repr__(self):
        return 'Location ' + str(self.location) + ' : {' + str(self.pre) + '} ' + self.target.name + '(' + str(
            *self.target.inparams) + ') {' + str(
            self.post) + '} :: ' + str(self.result)

    def check(self):
        # Does it satisfy P->Q ?
        # IF there is a solution to Not(P->Q) equiv to (P ^ Not Q) THEN
        #   unsat
        # ELSE
        #   no

        # Substitute constants with respective values
        pre = S.do_substitute(self.pre.condition, self.constants)
        post = S.do_substitute(self.post.guard, self.constants)

        logging.debug('Checking SAT for: ' + str(pre) + ' => ' + str(post))

        # Check the validity
        result = S.check_sat(self.variables, pre, post)

        logging.debug('result: ' + str(result) + '\n')
        return result


def remove_invalids(contracts):
    contracts[:] = [x for x in contracts if x.result]
    return contracts


def get_contracts(automaton, target, pre, wp):
    logging.debug('\n\nStarting Contract Generation')
    contracts = list()
    targetobj = Method(name_=target, params_=automaton.methods[target])
    # gather registers that would be needed for checking validity
    reg = list()
    for id_ in automaton.registers.keys():
        reg.append(automaton.registers[id_])
    logging.debug('List of defined registers: ' + str(reg))

    # gather defined constants that would be needed to
    # substitute constant values before checking validity
    const = list()
    for id_ in automaton.constants.keys():
        const.append((automaton.constants[id_][0], automaton.constants[id_][1]))
    logging.debug('List of defined constants: ' + str(const))

    # gather the list of parameters
    params = set()
    for x in automaton.methods[target]:
        params.add(S._int(x))

    for location in automaton.get_locations():
        logging.debug('\nGenerate contracts at ' + str(location))
        for precond in pre[location]:
            for post in wp[location]:
                logging.debug('Location: ' + str(location))
                logging.debug('Postcondition: ' + str(post))
                logging.debug('Weakest Precondition (consequent): ' + str(post.guard))
                logging.debug('Precondition: ' + str(precond))
                logging.debug('Precondition expression (antecedent): ' + str(precond.condition))

                for x in post.params:
                    params.add(x)

                contracts.append(Contract(target=targetobj,
                                          location=location,
                                          params=list(params),
                                          registers=reg,
                                          constants=const,
                                          precondition=precond,
                                          postcondition=post))
    logging.debug('\n\n============= GENERATED CONTRACT AT EACH LOCATION ===========')
    for item in contracts:
        logging.debug(item)

    # remove all the invalid contracts that results False
    contracts = remove_invalids(contracts)

    logging.debug('\n\n============= LIST OF VALID CONTRACTS ===========')
    for item in contracts:
        logging.debug(item)
    return contracts
