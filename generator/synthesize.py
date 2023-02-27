import copy
import itertools
import logging
from errors import *

import constraintsolver.solver as S
from constraintbuilder import build_str

automaton = None


def expr_to_contract(expr):
    expr = S.z3reftoStr(expr)
    strexpr = build_str(expr)

    for key in automaton.LITERALS.keys():
        if key.method.name.find('__equality__') != -1:
            strexpr = strexpr.replace(automaton.LITERALS[key], S.z3reftoStr(key.method.guard))
        else:
            # creating old value such as Not(a1)
            old_false = 'Not(' + automaton.LITERALS[key] + ')'
            new_false = '(' + str(key.method) + ' == FALSE)'
            old_true = automaton.LITERALS[key]
            new_true = '(' + str(key.method) + ' == TRUE)'
            strexpr = strexpr.replace(old_false, new_false)
            strexpr = strexpr.replace(old_true, new_true)

    return strexpr


def build_binary_expr(observers, expr=None):
    for observer in observers:
        if expr is None:
            if observer.output == automaton.OUTPUTS['TRUE']:
                expr = S._bool(observer.literal)
            else:
                expr = S._neg(S._bool(observer.literal))
        else:
            if observer.output == automaton.OUTPUTS['TRUE']:
                expr = S._and(expr, S._bool(observer.literal))
            else:
                expr = S._and(expr, S._neg(S._bool(observer.literal)))
    return S.do_simplify(expr)


def meet(pre, post, contract):
    if pre is not None:
        pre = S._or(pre, build_binary_expr(contract.monomial.observers))
        post = S._and(post,
                      S._implies(build_binary_expr(contract.monomial.observers), build_binary_expr([contract.wp])))
    else:
        pre = build_binary_expr(contract.monomial.observers)
        post = S._implies(build_binary_expr(contract.monomial.observers), build_binary_expr([contract.wp]))

    return pre, post


def join(pre, post, contract):
    if pre is not None:
        pre = S._and(pre, build_binary_expr(contract.monomial.observers))
        post = S._or(post, build_binary_expr(contract.wp))
    else:
        pre = build_binary_expr(contract.monomial.observers)
        post = build_binary_expr(contract.wp)

    return pre, post


def simplify(location):
    if not location.contracts:
        return
    logging.info('Contract for location :%s', location)
    print('Contract for location :', location)
    pre = None
    post = None
    for contract in location.contracts:
        pre, post = meet(pre, post, contract)
        # pre , post = join(pre, post, contract)

    pre = expr_to_contract(pre)
    post = expr_to_contract(post)
    # visited = list()
    # for first in location.contracts:
    #     if first in visited: continue
    #     result = None
    #     for second in location.contracts:
    #         if second not in visited and first.wp == second.wp and first.wp.output == second.wp.output:
    #             visited.append(second)
    #             if result is not None:
    #                 result = S._or(result, build_binary_expr(second))
    #             else:
    #                 result = build_binary_expr(second)
    #     pre = expr_to_contract(result)
    #     post = first.wp
    contract = '{' + pre + '} ' + str(automaton.TARGET) + ' {' + str(post) + '}'
    logging.info(contract)
    print(contract)
    logging.info('\n')
    print('\n')


def synthesize(config):
    global automaton
    automaton = config

    logging.debug('\n\nObserver to Boolean literal mapping:')
    logging.debug(config.LITERALS)
    logging.info('\n\n===================== FINAL CONTRACT =====================')
    print('\n\n===================== FINAL CONTRACT =====================')
    for location in automaton.LOCATIONS.values():
        simplify(location)
