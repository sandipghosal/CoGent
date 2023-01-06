import sys

from expression_builder.lexer import Lexer
from expression_builder.parser import Parser
from expression_builder.builder import Builder


def build_expr(automaton, transition):
    """ Process an expression and returns a solver object """
    lexer = Lexer(transition.guard)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, transition.guard).parse()
    builder = Builder(automaton, transition)
    expression = builder.build(tree)
    print(expression)