from constraintbuilder.builder import Builder
from constraintbuilder.lexer import Lexer
from constraintbuilder.parser import Parser
from constraintbuilder.stringparser import StringBuilder


def build_expr(expression):
    """ Process an expression and returns a solver object """
    lexer = Lexer(expression)
    tokens = lexer.create_tokens()
    tree = Parser(tokens, expression).parse()
    builder = Builder()
    exp = builder.build(tree)
    return exp



def build_str(expression):
    """
    Build a observer representation for a given string expression
    :param expression: string object of Z3 BoolRef
    :return: strng expression
    """
    lexer =Lexer(expression)
    tokens = lexer.create_tokens()
    expr = StringBuilder(tokens, expression).build()
    return expr