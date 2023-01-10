from constraint_builder.lexer import Lexer
from constraint_builder.parser import Parser
from constraint_builder.builder import Builder


def build_expr(expression, method, registers, constants):
    """ Process an expression and returns a solver object """
    lexer = Lexer(expression)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expression).parse()
    builder = Builder(method, registers, constants)
    return builder.build(tree)

