from constraint_builder.tokens import *


###############################
# AST
###############################


class AST(object):
    pass


class BinaryOp(AST):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOp(AST):
    def __init__(self, operator, expr):
        self.token = self.operator = operator
        self.expr = expr


class Boolean(AST):
    def __init__(self, token):
        self.token = token
        self.value = True if token.value == 'True' else False


class Variable(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


############################
# PARSER
############################

"""

============ Grammar of Expression ===================

expr :: term ((PLUS | MINUS) term )*

term :: factor ((MUL | DIV) factor)*

factor :: INT | FLOAT | LPAREN expr RPAREN | variable 

variable :: ID

"""


class Parser:

    def __init__(self, tokens, expression):
        self.tokens = tokens
        self.expression = expression
        self.index = 0

    def match(self, type_=None):
        if type_:
            if self.tokens[self.index].type in type_:
                if self.index < len(self.tokens)-1: self.index += 1
            else:
                raise ValueError()
        else:
            if self.index < len(self.tokens)-1: self.index += 1

    def factor(self):
        token = self.tokens[self.index]

        if token.type == PLUS:
            self.match()
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.match()
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == NOT:
            self.match()
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == BOOL:
            self.match()
            return Boolean(token)
        elif token.type == LPAREN:
            self.match()
            node = self.expr()
            self.match(RPAREN)
            return node
        elif token.type == ID:
            node = self.variable()
            self.match()  # for ID
            return node

    def term(self):
        # term: factor ((MUL|DIV) factor)*
        node = self.factor()

        while self.index < len(self.tokens) and self.tokens[self.index].type in (MUL, DIV, MOD):
            token = self.tokens[self.index]
            if token.type == MUL:
                self.match()
            elif token.type == DIV:
                self.match()
            elif token.type == MOD:
                self.match()

            node = BinaryOp(node, token, self.factor())

        return node

    def expr(self):
        # Arithmatic expression parser/interpreter
        # expr :: term ((PLUS | MINUS) term )*
        # term :: factor ((MUL | DIV) factor)*
        # factor :: INT | FLOAT | LPAREN expr RPAREN

        node = self.term()

        while self.index < len(self.tokens) and self.tokens[self.index].type in (PLUS, MINUS, AND, OR, NEQ, XOR, COMPARE):
            token = self.tokens[self.index]
            if token.type == PLUS:
                self.match()
            elif token.type == MINUS:
                self.match()
            elif token.type == AND:
                self.match()
            elif token.type == OR:
                self.match()
            elif token.type == NEQ:
                self.match()
            elif token.type == XOR:
                self.match()
            elif token.type == COMPARE:
                self.match()

            node = BinaryOp(node, token, self.term())

        return node

    def condition(self):
        # condition :: expr (COMPARE | LEQ | GEQ | GTHAN | LTHAN | NEQ ) expr :
        node = self.expr()

        token = self.tokens[self.index]

        if token.type in (COMPARE, LEQ, GEQ, GTHAN, LTHAN, NEQ):
            self.match()
            return BinaryOp(node, token, self.expr())
        else:
            return node

    def variable(self):
        # variable :: ID
        node = Variable(self.tokens[self.index])
        return node

    def parse(self):
        return self.condition()
