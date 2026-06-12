from common_imports import (
    dataclass, List, ABC, SOLVER
)

from constraintbuilder import LogicalExpression
from .predicate_manager import Predicate, PM


# =====================================================
# Conjunct Class
# =====================================================
@dataclass(repr=False)
class Conjunct:
    predicates: List[Predicate]

    def to_solver_expr(self):
        '''
        Convert this conjunct into:
        a0 AND a1 AND ...
        '''
        expr = SOLVER.bool_val(True)
        for pred in self.predicates:
            atom = PM.get_atom(pred)
            if pred.negated:
                atom = SOLVER._neg(atom)
            expr = SOLVER._and(expr, atom)
        return expr
    
    def __str__(self):
        parts = [str(p) for p in self.predicates]
        return " && ".join(parts)

    def __repr__(self):
        return self.__str__()



# =====================================================
# Base Condition Class
# =====================================================

class Condition(ABC):
    '''
    Base class for precondition and postcondition in contracts
    '''

    def __init__(self, expr: LogicalExpression):
        self.expr = expr

    def to_solver_expr(self):
        return self.expr.to_solver_expr()
    
    def __str__(self):
        return self.expr.text
    

# =====================================================
# Postcondition
# =====================================================


class Postcondition(Condition):
    '''
    Represents Q
    '''

    def __init__(self, predicate: Predicate, expr: LogicalExpression):
        self.predicate = predicate 
        # self.expr = expr  


    def __str__(self):
        return f'{self.predicate}'


# =====================================================
# Precondition
# =====================================================


class Precondition(Condition):
    '''
    Represents P

    Maintains:
    - expr: overall expression
    - dnf_clauses: List[List[Expression]] (each inner list is a conjunction)
    '''

    def __init__(self, conjuncts: List[Conjunct]):
        self.conjuncts = conjuncts
        self.expr = None  
    
    def to_solver_expr(self):
        if self.expr is not None:
            return self.expr
        result = SOLVER.bool_val(False)

        for conj in self.conjuncts:
            result = SOLVER._or(result, conj.to_solver_expr())

        self.expr = result
        return result



    def to_dnf(self):
        return self

    def get_clauses(self) -> List[List[LogicalExpression]]:
        '''
        Returns:
            [
                [a, !b],       # clause1
                [c]            # clause2
            ]

        '''
        # To be implemented
        pass

    def __str__(self):
        return  " || ".join(f"({c})" for c in self.conjuncts)
    

    def __repr__(self):
        return self.__repr__()
    
        # if not self.dnf_clauses:
        #     return PM.decode_expression(self.expr.text)
        
        # parts = []

        # for clause in self.dnf_clauses:
        #     if len(clause) == 1:
        #         parts.append(PM.decode_expression(str(clause[0])))
        #     else:
        #         parts.append("(" + " && ".join(PM.decode_expression(str(c)) for c in clause) + ")")

        # return " || ".join(parts)

