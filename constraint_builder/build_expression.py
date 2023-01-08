from constraint_builder.lexer import Lexer
from constraint_builder.parser import Parser
from constraint_builder.builder import Builder


def build_expr(automaton, transition, expression):
    """ Process an expression and returns a solver object """
    lexer = Lexer(expression)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expression).parse()
    # automaton required to get the registers, constants and parameters
    builder = Builder(automaton, transition)
    return builder.build(tree)

