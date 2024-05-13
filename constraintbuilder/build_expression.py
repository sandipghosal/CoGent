from constraintbuilder.builder import Builder
from constraintbuilder.expr_builder import LExprBuilder
from constraintbuilder.lexer import Lexer
from constraintbuilder.parser import Parser
from constraintbuilder.stringparser import StringBuilder

import re

operators = [
    r'==',
    r'!=',
    r'&&',
    r'&',
    r'and',
    r'And',
    r'\|\|',
    r'\|',
    r'or',
    r'Or',
    r'<=',
    r'>=',
    r'=>',
    r'<',
    r'>'
]

ignore = [
    r' +',
    r'\t+',
    r'\n'
]

operand = [r'[A-Za-z_][A-Za-z0-9_]*']

brackets = r'[\(\)]'


def match_brackets(expr):
    matches = re.findall(brackets, expr)
    if not matches:
        return False
    elif len(matches) % 2 != 0:
        raise ValueError()
    else:
        return True


def ignore_whitespaces(exp, col):
    for pattern in ignore:
        result = re.match(pattern, exp[col:])
        if result:
            col += result.end()
    return col


def get_matched(exp, regex, col):
    col = ignore_whitespaces(exp, col)
    for pattern in regex:
        op = re.match(pattern, exp[col:])
        if op:
            break
    if op:
        return op.group(), col + op.end()
    else:
        return '', col


def put_brackets(expressions, col):
    expr = ''
    # if equal number of brackets are present already
    # then return the original expression
    if match_brackets(expressions):
        return expressions

    # otherwise proceed with placing brackets around each clause
    while col < len(expressions):
        # append the next binary operator with expression computed in last iteration
        j, col = get_matched(expressions, operators, col)
        if j:
            expr = expr + ' ' + j
        lhs, col = get_matched(expressions, operand, col)
        op, col = get_matched(expressions, operators, col)
        rhs, col = get_matched(expressions, operand, col)
        expr = expr + ' (' + lhs + ' ' + op + ' ' + rhs + ') '

    return expr


def build_expr(expression):
    """ Process an expression and returns a BoolRef object """
    # put brackets if not there already around lhs and rhs for each binary operator
    expr = put_brackets(expression, 0)
    lexer = Lexer(expr)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expr).parse()
    builder = Builder()
    exp = builder.build(tree)
    return exp


def build_str(expression):
    """
    Build a observer representation for a given string expression
    :param expression: string object of Z3 BoolRef
    :return: strng expression
    """
    lexer = Lexer(expression)
    tokens = lexer.create_tokens()
    expr = StringBuilder(tokens, expression).build()
    return expr


def build_logical_expr(expression):
    """
    Convert a string expression to a logical expression of Boolean variables
    :param expression: string expression
    :return: BoolRef object

    >>> print(build_logical_expr('(a0 and a1) => false'))
    Implies(And(a0,a1), False)
    """
    expr = put_brackets(expression, 0)
    lexer = Lexer(expr)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expr).parse()
    builder = LExprBuilder()
    exp = builder.build(tree)
    return exp