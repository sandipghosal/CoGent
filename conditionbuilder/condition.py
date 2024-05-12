import smtsolvers.solver as S
from constraintbuilder import build_str
from smtsolvers.blalgebra import simplify


class Condition:
    def __init__(self, monomials, automaton):
        self.monomials = list()
        [self.monomials.append(x) for x in monomials]
        self.mapping = self.build_map(automaton.LITERALS)
        self.condition = self.get_condition()
        self.expression = self.get_expression(automaton)
        self.expr_text = self.get_text(automaton.LITERALS)

    def __repr__(self):
        return '{' + self.expr_text + '}'

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        for monomial in self.monomials:
            if monomial not in other.monomials:
                return False

        return True

    def __hash__(self):
        return hash(str(self))

    def __or__(self, other):
        """
        Disjunction of two conditions
        :param other:
        :return:
        """
        [self.monomials.append(x) for x in other.monomials]
        self.mapping.update(other.mapping)
        self.condition = S._or(self.condition, other.condition)
        self.expression = S._or(self.expression, other.expression)
        self.expr_text = self.get_text(self.mapping)
        return self

    def __and__(self, other):
        """
        Conjunction of two conditions
        :param other:
        :return:
        """
        [self.monomials.append(x) for x in other.monomials]
        self.mapping.update(other.mapping)
        self.condition = S._and(self.condition, other.condition)
        self.expression = S._and(self.expression, other.expression)
        self.expr_text = self.get_text(self.mapping)
        return self

    def implies(self, other):
        """
        Perform implication of self to other
        :param other:
        :return:
        """
        [self.monomials.append(x) for x in other.monomials]
        self.mapping.update(other.mapping)
        self.condition = S._implies(self.condition, other.condition)
        self.expression = S._implies(self.expression, other.expression)
        self.expr_text = self.get_text(self.mapping)
        return self

    def substitute(self, subs):
        """ substitute the condition wrt. subs"""
        self.condition = S.do_substitute(self.condition, subs)

    def build_map(self, literals):
        """
        Build the mapping from observer method to literal for the current monomial
        :param literals: global dict of literals from config
        """
        mapping = dict()
        for monomial in self.monomials:
            for observer in monomial.observers:
                if not observer.literal:
                    return mapping
                mapping[observer] = literals[observer]
        return mapping

    def get_text(self, literals, strexpr=None):
        expr = S.z3reftoStr(self.expression)
        strexpr = build_str(expr) if strexpr is None else strexpr
        # perform simplification each time a condition object is created
        # strexpr = str(simplify(strexpr))
        if strexpr in ('True', 'False'):
            return strexpr
        for key in literals.keys():
            if key.method.name.find('__equality__') != -1:
                string = ''
                if len(key.method.inputs) == 1:
                    string = key.method.inputs[0]
                else:
                    string = '(' + key.method.inputs[0] + ' == ' + key.method.inputs[1] + ')'

                strexpr = strexpr.replace(literals[key], string)

            elif key.method.name.find('__ltequality__') != -1:
                string = ''
                if len(key.method.inputs) == 1:
                    string = key.method.inputs[0]
                else:
                    string = '(' + key.method.inputs[0] + ' < ' + key.method.inputs[1] + ')'

                strexpr = strexpr.replace(literals[key], string)
            elif key.method.name.find('__gtequality__') != -1:
                string = ''
                if len(key.method.inputs) == 1:
                    string = key.method.inputs[0]
                else:
                    string = '(' + key.method.inputs[0] + ' > ' + key.method.inputs[1] + ')'

                strexpr = strexpr.replace(literals[key], string)

            else:
                # creating old value such as Not(a1)
                old_false = 'Not(' + literals[key] + ')'
                new_false = 'Not(' + str(key.method) + ')'
                # new_false = '(' + str(key.method) + ' == FALSE)'
                old_true = literals[key]
                new_true = '(' + str(key.method) + ')'
                # new_true = '(' + str(key.method) + ' == TRUE)'
                strexpr = strexpr.replace(old_false, new_false)
                strexpr = strexpr.replace(old_true, new_true)

        return strexpr

    def get_condition(self):
        assert len(self.monomials) == 1
        return self.monomials[0].condition

    def get_expression(self, automaton, expr=None):
        assert len(self.monomials) == 1
        for observer in self.monomials[0].observers:
            if observer.method.name in ('True', 'False'):
                expr = S._boolval(observer.method.guard)
            elif expr is None:
                if observer.output == automaton.OUTPUTS['TRUE']:
                    expr = S._bool(observer.literal)
                else:
                    expr = S._neg(S._bool(observer.literal))
            else:
                if observer.output == automaton.OUTPUTS['TRUE']:
                    expr = S._and(expr, S._bool(observer.literal))
                else:
                    expr = S._and(expr, S._neg(S._bool(observer.literal)))
        return S.do_simplify(expr)

    def update(self, automaton):
        self.mapping = self.build_map(automaton.LITERALS)
        self.expression = self.get_expression(automaton)
        self.expr_text = self.get_text(self.mapping)
