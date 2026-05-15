from constraintbuilder.builder import Builder
#from constraintbuilder.expr_builder import LExprBuilder
from constraintbuilder.lexer import Lexer
from constraintbuilder.parser import Parser
from constraintbuilder.stringparser import StringBuilder

import re

from customlogger import getlogger
log = getlogger(__name__)

from solvers.factory import get_solver
solver = get_solver()

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

operand = [r'[A-Za-z_][A-Za-z0-9_]*|[0-9]*']

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


def normalize_text(s: str) -> str:
    # remove whitespace and normalize parentheses spacing
    s = re.sub(r"\s+", "", s)
    return s

def equals_syntax(e1, e2) -> bool:
    # check if two Expression objects e1 and e2 are syntactically same
    if isinstance(e1, Expression) != isinstance(e2, Expression):
        log.debug('Either e1 or e2 is not of Expression type')
        return False
    if sorted(normalize_text(e1.text)) == sorted(normalize_text(e2.text)):
        log.debug('Expressions '+ e1.text + ' and ' + e2.text + ' are syntactically same')
        return True
    

def equals_semantic(e1, e2) -> bool:
    # check if two Expression objects e1 and e2 are semantically same
    '''
    Check logical equivalence using the solver.
    '''
    if isinstance(e1, Expression) != isinstance(e2, Expression):
        log.debug('Either e1 or e2 is not of Expression type')
        return False
    if solver.check_equivalence(solver._ne(e1.solver_expr, e2.solver_expr)) is True:
        log.debug('Expressions '+ e1.text + ' and ' + e2.text + ' are semantically same')
        return True



def build_expr(expression):
    """ Process an expression and returns a Solver object """
    # put brackets if not there already around lhs and rhs for each binary operator
    log.debug('Get the solver object for expression: '+ expression)
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
    #builder = LExprBuilder()
    builder = Builder()
    exp = builder.build(tree)
    return exp



###############################################
# Expression (Solver Specific Logical Expression)
###############################################

from dataclasses import dataclass, field
from typing import Optional, Any

@dataclass
class Expression:
    '''
    Solver-independent logical and arithmetic expression
    '''
    text: str
    solver_expr: Any = field(init=False, default=None)

    def to_solver_expr(self):
        '''
        Convert string expression to solver-specific representation.
        Cached after first build.
        '''
        if self.solver_expr is None:
            self.solver_expr = build_expr(self.text)
        return self.solver_expr
    
    def __eq__(self, other) -> bool:
        # check if syntactically and sematically equal
        log.debug("Checking if " + self.text + " is same as " + other.text)
        return equals_semantic(self, other)

    def __hash__(self):
        return hash(normalize_text(self.text))
    
    def __str__(self):
        return self.text