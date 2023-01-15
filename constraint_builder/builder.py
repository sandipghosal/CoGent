import sys

from constraint_builder.tokens import *
from constraintsolver.solver import *


class NodeVisitor:
    def visit(self, node):
        # dynamically create the name of the function
        _func_name = 'visit_' + type(node).__name__

        # match the function name and execute the method
        # otherwise execute generic_visit()
        visitor = getattr(self, _func_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')


class Builder(NodeVisitor):

    def __init__(self, method_, registers_, constants_):
        self.method = method_
        self.registers = registers_
        self.constants = constants_

    def visit_BinaryOp(self, node):
        if node.operator.type == OR:
            return get_or(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == AND:
            return get_and(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == NEQ:
            return get_neq(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == COMPARE:
            return self.visit(node.left) == self.visit(node.right)
        else:
            raise ValueError()

    def visit_UnaryOp(self, node):
        if node.operator.type == NOT:
            return get_neg(self.visit(node.expr))
        else:
            raise ValueError()

    def visit_Boolean(self, node):
        if node.token.type == BOOL:
            return get_bool_object(node.value)
        else:
            raise ValueError()

    def visit_Variable(self, node):
        if node.value in self.constants:
            return self.constants[node.value][0]
        elif node.value in self.registers:
            return self.registers[node.value]
        elif self.method.params is not None \
                and node.value in self.method.params:
            return get_int_object(node.value)
        elif self.method.outputs is not None \
                and node.value in self.method.outputs:
            return get_int_object(node.value)
        else:
            print(node.value, 'No found')
            sys.exit(0)

    def build(self, tree):
        return self.visit(tree)
        # return self.expression.add(self.visit(tree))
