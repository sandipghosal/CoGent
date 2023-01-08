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

    def __init__(self, automaton_, transition_):
        self.automaton = automaton_
        self.transition = transition_

    def visit_BinaryOp(self, node):
        if node.operator.type == OR:
            return Or(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == AND:
            return And(self.visit(node.left), self.visit(node.right))
        elif node.operator.type == NEQ:
            return Not(self.visit(node.left) == self.visit(node.right))
        elif node.operator.type == COMPARE:
            return self.visit(node.left) == self.visit(node.right)
        else:
            raise ValueError()

    def visit_UnaryOp(self, node):
        if node.operator.type == NOT:
            print(Not(self.visit(node.expr)))
        else:
            raise ValueError()

    def visit_Boolean(self, node):
        if node.token.type == BOOL:
            return node.value
        else:
            raise ValueError()

    def visit_Variable(self, node):
        if node.value in self.automaton.constants:
            return self.automaton.constants[node.value][0]
        elif node.value in self.automaton.registers:
            return self.automaton.registers[node.value]
        elif node.value in self.transition.method.paramIDs:
            pid = self.transition.method.name + '.' + node.value
            return get_object(pid)
        else:
            raise ValueError()

    def build(self, tree):
        return self.visit(tree)
        # return self.expression.add(self.visit(tree))
