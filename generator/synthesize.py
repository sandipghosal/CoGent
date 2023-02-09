import logging
from errors import *

import constraintsolver.solver as S
from constraintbuilder import build_str

automaton = None
contracts = None
literals = dict()


class SynthesizedContract:
    def __init__(self, pre, post, target):
        self.pre = pre
        self.post = post
        self.target = target

    def __repr__(self):
        return '{' + self.pre + '} ' + self.target.name + '(' + \
            str(*self.target.inparams) + ') {' + self.post + '}'


class Literal:
    def __init__(self, condition):
        if condition.output == 'FALSE':
            condition.guard = S._neg(condition.guard)
            condition.output = 'TRUE'
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
                expr = S._and(expr, S._neg(S._bool(literals[Literal(observer)])))
    return expr


def expr_to_contract(expr):
    expr = S.z3reftoStr(expr)
    strexpr = build_str(expr)
    for key in literals.keys():
        if key.condition.name == '__equality__':
            strexpr = strexpr.replace(literals[key], S.z3reftoStr(key.condition.guard))
        else:
            # creating old value such as Not(a1)
            old_false = 'Not(' + literals[key] + ')'
            new_false = '(' + str(key) + ' == False)'
            old_true = literals[key]
            new_true = '(' + str(key) + ' == True)'
            strexpr = strexpr.replace(old_false, new_false)
            strexpr = strexpr.replace(old_true, new_true)

    return strexpr


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


def list_of_postconditions():
    l = list()
    for contract in contracts:
        if contract.post not in l:
            l.append(contract.post)
    return l


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

    for contract in contracts:
        create_literals(contract)

    logging.debug('Observer to Boolean literal mapping:')
    logging.debug(literals)

    # fetch target from any contract say from the first one
    try:
        target = contracts[0].target
    except:
        raise ValueNotFound('Contract not found')

    # obtain the list of unique Postcondtion objects
    posts = list_of_postconditions()
    # list to hold all synthesized contracts

    # expr_true = contract_wrt_output('I_contains', 'TRUE')
    # expr_false = contract_wrt_output('I_contains', 'FALSE')
    # check(expr_true, expr_false)

    syn_contract = list()
    for condition in posts:
        expr = contract_wrt_output(condition.name, condition.output)
        logging.debug('Contract for ' + str(condition))
        logging.debug(S.z3reftoStr(expr))
        pre = expr_to_contract(expr)
        post = str(condition)
        result = condition.output
        syn_contract.append(SynthesizedContract(pre, post, target))

    return syn_contract


def check(expr_true, expr_false):
    params = list()
    for key in literals.keys():
        params.append(S._bool(literals[key]))

    # Do negation of the implication
    expr = S._and(expr_true, S._neg(expr_false))

    # Add exists parameters
    expr = S._exists(params, expr)

    # Check the validity
    result = S.do_check(expr)

    print(result)
