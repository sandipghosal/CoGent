
from constraintbuilder.tokens import *
from errors import *

from solvers.factory import get_solver
solver = get_solver()

from customlogger import getlogger
log = getlogger(__name__)

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

    def visit_BinaryOp(self, node):
        if node.operator.type == OR:
            # return (self.visit(node.left))._or(self.visit(node.right))
            return solver._or(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == AND:
            # return (self.visit(node.left))._and(self.visit(node.right))
            return solver._and(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == NEQ:
            # return (self.visit(node.left))._ne(self.visit(node.right))
            return solver._ne(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == COMPARE:
            return solver._eq(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == GTHAN:
            return solver._gt(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == LTHAN:
            return solver._lt(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == GEQ:
            return solver._geq(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == LEQ:
            return solver._leq(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == IMPLY:
            return solver.implies(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == PLUS:
            return solver._add(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == MINUS:
            return solver._sub(self.visit(node.left), self.visit(node.right))
        else:
            log.critical('Node '+ str(node) + ' not found')
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_UnaryOp(self, node):
        if node.operator.type == NOT:
            return solver._neg(self.visit(node.expr))
            # return get_neg(self.visit(node.expr))
        else:
            log.critical('Node '+ str(node) + ' not found')
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_Boolean(self, node):
        if node.token.type == BOOL:
            return solver.bool_val(node.value)
            # return get_bool_object(node.value)
        else:
            log.critical('Node '+ str(node) + ' not found')
            raise ValueNotFound('Node not found: ' + str(node))

    def visit_Variable(self, node):
        return solver.int(node.value)

    def visit_IntConstant(self, node):
        return solver.int_val(node.value)


    def build(self, tree):
        return self.visit(tree)
        # return self.expression.add(self.visit(tree))
