import re

from constraint_builder.tokens import *


######################
# TOKEN
######################

class Token(object):
    """ Class for all token objects created for a logical expression """

    def __init__(self, type_, value_=None):
        self.type = type_
        self.value = value_

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'


##############################
# LEXER
##############################

class Lexer:
    """ Class responsible for tokenizing an input logical expression """

    def __init__(self, expression_):
        self.expression = expression_
    def create_tokens(self):
        """ Create a list of token objects for a given expression """
        # create an empty token list
        tokens = list()

        # initialize column with zero
        column = 0

        # while column is less than length of the expression
        while column < len(self.expression):

            # initialize result with None
            result = None

            # foreach expr in token_expr
            for expr in token_expr:

                # initialize pattern and type from the expr
                pattern, type_ = expr

                # update the result on finding a matched pattern
                result = re.match(pattern, self.expression[column:])

                # if result is not None
                if result:
                    # calculate length of the matched pattern and initialize into length
                    length = result.end()

                    # initialize a token object
                    token = Token(type_, result.group(0))

                    # add the token into the list of tokens
                    tokens.append(token)

                    # advance the column number by the length
                    column += length

                    # exit from the for loop
                    break

            if result is None:
                raise ValueError()

        # optimize the list of tokens
        tokens = self.__optimize_tokens(tokens)

        return tokens

    def __optimize_tokens(self, tokens):
        """ Removes irrelevant tokens such as SPACE, TAB
        and returns a reduced list of tokens """
        index = 0

        while index < len(tokens):
            if tokens[index].type in (SPACE, TAB, NEWLINE, EOF):
                tokens.pop(index)
                continue
            index = index + 1

        return tokens
