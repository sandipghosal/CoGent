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


def build_binary_expr(contract, expr=None):
    for observer in contract.monomial.observers:
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


def simplify(location):
    print('Contract for location :', location)
    visited = list()
    for first in location.contracts:
        result = None
        for second in location.contracts:
            if second not in visited and first.wp == second.wp and first.wp.output == second.wp.output:
                visited.append(second)
                if result is not None:
                    result = S._or(result, build_binary_expr(second, result))
                else:
                    result = build_binary_expr(second, result)
        pre = expr_to_contract(result)
        post = first.wp
        print('{' + pre + '} ' + str(automaton.TARGET) + ' {' + str(post) + '}')
    print('\n')


def synthesize(config):
    global automaton
    automaton = config

    logging.debug('\n\nObserver to Boolean literal mapping:')
    logging.debug(config.LITERALS)
    logging.debug('\n\n===================== FINAL CONTRACT =====================')
    for location in automaton.LOCATIONS.values():
        simplify(location)


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
