import constraintsolver.solver as S
from constraintbuilder.tokens import *
from errors import *


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

    def __init__(self, registers_, constants_):
        # self.method = method_
        self.registers = registers_
        self.constants = constants_

    def visit_BinaryOp(self, node):
        if node.operator.type == OR:
            # return (self.visit(node.left))._or(self.visit(node.right))
            return S._or(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == AND:
            # return (self.visit(node.left))._and(self.visit(node.right))
            return S._and(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == NEQ:
            # return (self.visit(node.left))._ne(self.visit(node.right))
            return S._ne(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == COMPARE:
            return S._eq(self.visit(node.left), self.visit(node.right))
        else:
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_UnaryOp(self, node):
        if node.operator.type == NOT:
            return S._neg(self.visit(node.expr))
            # return get_neg(self.visit(node.expr))
        else:
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_Boolean(self, node):
        if node.token.type == BOOL:
            return S._bool(node.value)
            # return get_bool_object(node.value)
        else:
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_Variable(self, node):
        if node.value in self.constants:
            return self.constants[node.value][0]
        elif node.value in self.registers:
            return self.registers[node.value]
        # elif self.method.inparams is not None \
        #         and node.value in self.method.inparams:
        #     return S._int(node.value)
        # elif self.method.outparams is not None \
        #         and node.value in self.method.outparams:
        #     return S._int(node.value)
        else:
            return S._int(node.value)
            # raise ValueNotFound('Node not found: ' + str(node))

    def build(self, tree):
        return self.visit(tree)
        # return self.expression.add(self.visit(tree))
