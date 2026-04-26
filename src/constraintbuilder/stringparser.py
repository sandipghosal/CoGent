
from constraintbuilder.tokens import *


class StringBuilder:

    def __init__(self, tokens, expression):
        self.tokens = tokens
        self.expression = expression
        self.index = 0
        self.stack = list()

    def match(self, type_=None):
        if type_:
            if self.tokens[self.index].type in type_:
                if self.index < len(self.tokens) - 1: self.index += 1
            else:
                raise ValueError()
        else:
            if self.index < len(self.tokens) - 1: self.index += 1

    def build(self):
        for index in range(len(self.tokens) - 1, -1, -1):
            # when the token is not an operator
            if self.tokens[index].type not in (AND, OR, NOT):
                self.stack.append(self.tokens[index].value)

            # when token is an operator
            else:
                operator = None
                if self.tokens[index].type == AND:
                    operator = 'and'
                elif self.tokens[index].type == OR:
                    operator = 'or'
                else:
                    operator = 'Not'

                expr = ''

                if operator == 'Not':
                    expr = 'Not'
                    # should pop the last entered LPAREN
                    item = self.stack.pop()
                    while item not in ')':
                        expr = expr + item
                        item = self.stack.pop()
                    # should fetch till an RPAREN is encountered
                    expr = expr + item
                    self.stack.append(expr)
                else:
                    # should pop the last entered LPAREN
                    item = self.stack.pop()
                    while item not in ')':
                        if item not in ',':
                            expr = expr + item
                        else:
                            expr = expr + ' ' + operator + ' '
                        item = self.stack.pop()
                    # should fetch till an RPAREN is encountered
                    expr = expr + item
                    self.stack.append(expr)

        return self.stack.pop()
