from common_imports import(
    dataclass, copy, Any, ABC,
    abstractmethod, re, log
)

from ramodel import Method, OutputKind
from expressions import Expression, LogicalExpression

# =====================================================
# Predicate Class
# =====================================================

class Predicate(ABC):

    negated: bool = False

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def get_condition(self) -> str:
        pass

    @abstractmethod
    def negate(self):
        pass

    def normalize(self, expr: str) -> str:
        pattern = r'(-?\d+)\s*\+\s*([A-Za-z_]\w*)'
        return re.sub(
            pattern,
            lambda m: f"{m.group(2)}{int(m.group(1)):+d}",
            expr
        )

    # def to_expression(self):
    #     encoded = PM.encode_expression(self.to_string())

    #     if self.negated:
    #         return LogicalExpression(f"!({encoded})")

    #     return LogicalExpression(encoded)

    def __str__(self):
        base = self.to_string()

        if self.negated:
            return f"!({base})"

        return f"{base}"


    def __repr__(self):
        return self.__str__()


# =====================================================
# BooleanObserverPredicate Class
# =====================================================


@dataclass(repr=False)
class BooleanObserverPredicate(Predicate):

    observer: Method
    negated: bool = False


    def get_condition(self):
        return self.observer.condition


    def negate(self):
        pred = copy.deepcopy(self)
        pred.observer.output = not pred.observer.output
        pred.observer.output_kind = OutputKind.TRUE if pred.observer.output else OutputKind.FALSE
        pred.negated = not pred.negated
        return pred


    def to_string(self):
        return str(self.observer)
    

# =====================================================
# RelationalPredicate Class
# =====================================================

@dataclass(repr=False)
class RelationalPredicate(Predicate):
    lhs: Any
    op: str
    rhs: Any
    negated: bool = False

    # def get_condition(self):
    #     return self.observer.condition


    def negate(self):
        pred = copy.deepcopy(self)
        pred.negated = not pred.negated
        return pred
    
    def get_condition(self) -> Expression:
        expr = None
        if isinstance(self.lhs, Method):
            if not self.lhs.output_params[0]:
                log.error(f'LHS of RelationalObserver {self.lhs} does not have output parameter')
                ValueError("LHS of RelationalObserver does not have output parameter")
            else:
                expr = Expression(
                    f"{self.lhs.output}"
                    f" {self.op} "
                    f"{self.rhs}"
                )
        else:
            # lhs = self.lhs
            # rhs = self.rhs
            # if isinstance(self.lhs, Expression):
            #     lhs = f"({self.lhs})"
            # if isinstance(self.rhs, Expression):
            #     rhs = f"({self.rhs})"
            expr = Expression(
                f"{self.lhs}"
                f" {self.op} "
                f"{self.rhs}"
            )
        return expr.negate() if self.negated else expr

        # elif isinstance(self.lhs, Variable) and isinstance(self.rhs, Expression):
        #     expr = Expression(
        #         f"{self.lhs}"
        #         f" {self.op} "
        #         f"{self.rhs.text}"
        #     )
        # elif isinstance(self.lhs, Expression) and isinstance(self.rhs, Variable):
        #     expr = Expression(
        #         f"{self.lhs.text}"
        #         f" {self.op} "
        #         f"{self.rhs}"
        #     )     
        # elif isinstance(self.lhs, Variable) and isinstance(self.rhs, Variable):
        #     expr = Expression(
        #         f"{self.lhs}"
        #         f" {self.op} "
        #         f"{self.rhs}"
        #     )

        
        

    def to_string(self):
        return (
            f"{self.lhs}"
            f" {self.op} "
            f"{self.rhs}"
        )


# =====================================================
# BooleanPredicate Class
# =====================================================

@dataclass(repr=False)
class BooleanPredicate(Predicate):
    expr: Expression

    def get_condition(self):
        return self.expr
    
    def to_string(self):
        return str(self.expr)
    
    def negate(self):
        pred = copy.deepcopy(self)
        pred.negated = not pred.negated

        return pred