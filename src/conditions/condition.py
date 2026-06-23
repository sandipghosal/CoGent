from common_imports import (
    dataclass, ABC, abstractmethod, List, ABC, SOLVER
)

from expressions import LogicalExpression
from predicates import Predicate, PM



class BoolExpr(ABC):
    """
    Base class for boolean expressions over predicates
    """

    @abstractmethod
    def precedence(self) -> int:
        pass

    @abstractmethod
    def to_solver_expr(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()


@dataclass(repr=False)
class Atom(BoolExpr):
    predicate: Predicate

    def to_solver_expr(self):
        atom = PM.get_atom(self.predicate)
        return SOLVER._neg(atom) if self.predicate.negated else atom
    
    def precedence(self):
        return 4

    def __str__(self):
        return str(self.predicate)
    
    def __repr__(self):
        return self.__str__()
    

@dataclass(repr=False)
class Not(BoolExpr):
    expr: BoolExpr

    def to_solver_expr(self):
        return SOLVER._neg(self.expr.to_solver_expr())
    
    def precedence(self):
        return 3

    def __str__(self):
        if isinstance(self.expr, Atom):
            return f"!{self.expr}"
        return f"!({self.expr})"
        # if self.expr.precedence() < self.precedence():
        #     return f"!({self.expr})"
        # else:
        #     return f"!{self.expr}"
    
    def __repr__(self):
        return self.__str__()
    

@dataclass(repr=False)
class And(BoolExpr):
    terms: List[BoolExpr]

    def precedence(self):
        return 2

    def to_solver_expr(self):
        result = SOLVER.bool_val(True)
        for t in self.terms:
            result = SOLVER._and(result, t.to_solver_expr())
        return result

    def __str__(self):
        parts = []
        for t in self.terms:
            if t.precedence() < self.precedence():
                parts.append(f"({t})")
            else:
                parts.append(str(t))
        return " && ".join(parts)
    
    def __repr__(self):
        return self.__str__()


@dataclass(repr=False)
class Or(BoolExpr):
    terms: List[BoolExpr]

    def to_solver_expr(self):
        result = SOLVER.bool_val(False)
        for t in self.terms:
            result = SOLVER._or(result, t.to_solver_expr())
        return result
    
    def precedence(self):
        return 1

    def __str__(self):
        parts = []
        for t in self.terms:
            if t.precedence() < self.precedence():
                parts.append(f"({t})")
            elif isinstance(t, And):
                parts.append(f"({t})")
            else:
                parts.append(str(t))
        return " || ".join(parts)
    
    def __repr__(self):
        return self.__str__()
    

@dataclass(repr=False)
class Implies(BoolExpr):
    antecedent: BoolExpr
    consequent: BoolExpr

    def to_solver_expr(self):
        return SOLVER.implies(
            self.antecedent.to_solver_expr(),
            self.consequent.to_solver_expr()
        )

    def __str__(self):
        return f"({self.antecedent}) -> ({self.consequent})"
    
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

class Postcondition:
    """
    Postcondition is a Boolean expression over predicates
    """
    def __init__(self, expr: BoolExpr):
        self.expr = expr

    def to_solver_expr(self):
        return self.expr.to_solver_expr()

    def __str__(self):
        return f"{self.expr}"
    
    def __repr__(self):
        return self.__str__()



# =====================================================
# Precondition
# =====================================================

class Precondition:
    """
    Precondition is just a Boolean expression over predicates
    """

    def __init__(self, expr: BoolExpr):
        self.expr = expr

    def to_solver_expr(self):
        return self.expr.to_solver_expr()

    def __str__(self):
        return str(self.expr)

    def __repr__(self):
        return self.__str__()


