import logging

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
        if self.check(params, registers, constants) == S._sat():
            self.result = 'False'
        else:
            self.result = 'True'
        # self.result = self.check(params, registers, constants)
        # obtain precondition from the observers
        # check of precondition => weakestpre is satisfied and store into self.result

    def __repr__(self):
        return 'Location ' + str(self.location) + ' : {' + str(self.pre) + '} ' + self.target.name + '(' + str(
            *self.target.inparams) + ') {' + str(
            self.post) + '} :: ' + str(self.result)

    def check(self, params, registers, constants):
        # Does it satisfy P->Q ?
        # IF there is a solution to Not(P->Q) equiv to (P ^ Not Q) THEN
        #   no
        # ELSE
        #   yes

        # First derive the quantifier eliminated expresseion
        # qe_expr = None
        # if self.post.condition.weakestpre not in (S._bool(True), S._bool(False)):
        #     qe_expr = S.elminate(registers, self.post.condition.weakestpre)
        #
        # logging.debug('quantifier eliminated expression:', qe_expr)

        # if qe_expr is not None:
        #     for i in range(qe_expr[0].num_args()):
        #         print(qe_expr[0].arg(i))

        expr = S._implies(self.pre.condition, self.post.guard)

        logging.debug('Checking SAT for: ' + str(expr))

        # Do negation of the implication
        expr = S._and(self.pre.condition, S._neg(self.post.guard))

        logging.debug('Negation of implication: ' + str(expr))

        # Substitute constants with respective values
        expr = S.do_substitute(expr, constants)

        logging.debug('After constant substitution: ' + str(expr))

        # Add forall parameters
        # expr = S._forall(params, expr)
        # expr = S._forall(registers, expr)

        # logging.debug('After adding for all: ' + str(expr))

        params = params + registers

        # Add exists parameters and registers
        expr = S._exists(params, expr)

        # expr = S._forall(params, expr)

        logging.debug('Final expression before checking SAT: ' + str(expr))

        # Check the validity
        result = S.do_check(expr)

        logging.debug('result: ' + str(result) + '\n')
        return result



def get_contract(automaton, target, pre, wp):
    logging.debug('\n\nStarting Contract Generation')
    contract = list()
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
        logging.debug('\nGenerate contract at ' + str(location))
        for precond in pre[location]:
            for post in wp[location]:
                logging.debug('Location: ' + str(location))
                logging.debug('Postcondition: ' + str(post))
                logging.debug('Weakest Precondition (consequent): ' + str(post.guard))
                logging.debug('Precondition: ' + str(precond))
                logging.debug('Precondition expression (antecedent): ' + str(precond.condition))

                for x in post.params:
                    params.add(x)

                contract.append(Contract(target=targetobj,
                                         location=location,
                                         params=list(params),
                                         registers=reg,
                                         constants=const,
                                         precondition=precond,
                                         postcondition=post))
    return contract