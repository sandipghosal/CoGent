from constraintbuilder.builder import Builder
from constraintbuilder.lexer import Lexer
from constraintbuilder.parser import Parser


def build_expr(expression):
    """ Process an expression and returns a solver object """
    lexer = Lexer(expression)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expression).parse()
    builder = Builder()
    exp = builder.build(tree)
    return exp
