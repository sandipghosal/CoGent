import logging
import re

import constraintsolver.solver as S
from constraintbuilder import build_str

automaton = None
contracts = None
literals = dict()

class SynthesizedContract:
    def __init__(self, pre, post, result):
        self.pre = pre
        self.post = post
        self.result = result


class Literal:
    def __init__(self, condition):
        self.condition = condition
        self.params = self.to_string(condition.params)

    def to_string(self, paramlist):
        params = list()
        for item in paramlist:
            # parameter list in other could be a list of ArithRef
            if not isinstance(item, str):
                params.append(S.z3reftoStr(item))
            else:
                params.append(item)
        return params

    def __eq__(self, other):
        return self.condition.name == other.condition.name and self.params == other.params

    def __hash__(self):
        return hash(self.condition.name + ' ' + str(self.params))

    def __repr__(self):
        if self.condition.name == '__equality__':
            return S.z3reftoStr(self.condition.guard)
        else:
            return self.condition.name + '(' + str(*self.params) + ') '
        # return self.condition.name + ' ' + str(self.params)


def build_binary_expr(contract, expr=None):
    for observer in contract.pre.observers:
        if expr is None:
            if observer.output == 'TRUE':
                expr = S._bool(literals[Literal(observer)])
            else:
                expr = S._neg(S._bool(literals[Literal(observer)]))
        else:
            if observer.output == 'TRUE':
                expr = S._and(expr, S._bool(literals[Literal(observer)]))
            else:
                expr = S._and(expr, S._bool(literals[Literal(observer)]))
    return expr


def expr_to_contract(expr):
    expr = S.z3reftoStr(expr)
    strexpr = build_str(expr)
    for key in literals.keys():
        if key.condition.name == '__equality__':
            expr = strexpr.replace(literals[key], S.z3reftoStr(key.condition.guard))
        else:
            oldvalue = strexpr.replace
    print(expr)



def contract_wrt_output(observer, output):
    expr = None
    for index in range(len(contracts)):
        if contracts[index].post.name == observer \
                and contracts[index].post.output == output:
            if expr is None:
                expr = build_binary_expr(contracts[index])
            else:
                expr = S._or(expr, build_binary_expr(contracts[index]))

    expr = S.do_simplify(expr)
    return expr


def create_literals(contract):
    global literals
    for observer in contract.pre.observers:
        newobject = Literal(observer)
        if newobject not in literals.keys():
            literals[newobject] = 'a' + str(len(literals))
    # return literals


def synthesize(automaton_, contracts_):
    global automaton, contracts
    automaton = automaton_
    contracts = contracts_
    # literals = dict()
    for contract in contracts:
        create_literals(contract)

    for observer in automaton.get_observers():
        expr = contract_wrt_output(observer, 'TRUE')
        # expr_false = contract_wrt_output(observer, binary, 'FALSE')

        logging.debug('Final contract for ' + observer + ' == TRUE :')
        logging.debug(S.z3reftoStr(expr))
        logging.debug('\n\n')
    expr_to_contract(expr)
