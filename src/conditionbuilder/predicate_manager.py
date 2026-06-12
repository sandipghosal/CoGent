print("Loading predicate_manager")

from common_imports import(
    Optional, dataclass, Dict, copy,
    ABC, abstractmethod, re, SOLVER
)

from ramodel import OutputKind, Method
from constraintbuilder import Expression, LogicalExpression



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

    def to_expression(self):
        encoded = PM.encode_expression(self.to_string())

        if self.negated:
            return LogicalExpression(f"!({encoded})")

        return LogicalExpression(encoded)

    def __str__(self):
        base = self.to_string()

        if self.negated:
            return f"!({base})"

        return base


    def __repr__(self):
        return self.__str__()


# =====================================================
# ObserverPredicate Class
# =====================================================

@dataclass(repr=False)
class ObserverPredicate(Predicate):

    observer: Method
    op: Optional[str] = None
    negated: bool = False

    def get_condition(self) -> Expression:
        if self.observer.output_kind is OutputKind.VALUE:
            return Expression(
                f"{self.observer.output_params[0]} "
                f"{self.op} "
                f"{self.observer.output}"
            )
        else:
            return self.observer.condition

    def negate(self):

        pred = copy.deepcopy(self)

        pred.negated = not pred.negated

        if pred.observer.output_kind is OutputKind.TRUE:
            pred.observer.output_kind = OutputKind.FALSE

        elif pred.observer.output_kind is OutputKind.FALSE:
            pred.observer.output_kind = OutputKind.TRUE

        return pred

    def to_string(self):

        if self.observer.output_kind in (
            OutputKind.TRUE,
            OutputKind.FALSE,
        ):
            return str(self.observer)

        if self.observer.output_kind is OutputKind.VALUE:
            return (
                f"{self.observer} "
                f"{self.op} "
                f"{self.observer.output_params[0]}"
            )

        return ""



# =====================================================
# EqualityPredicate Class
# =====================================================


@dataclass(repr=False)
class EqualityPredicate(Predicate):

    expr: Expression
    negated: bool = False

    def get_condition(self):
        return self.expr

    def negate(self):

        pred = copy.deepcopy(self)
        pred.negated = not pred.negated

        return pred

    def to_string(self):
        base = str(self.expr)
        return self.normalize(base)
        # return str(self.expr)
    
# =====================================================
# EqualityPredicate Class
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
    



# =====================================================
# Predicate Symbol
# =====================================================

from typing import Any

@dataclass
class PredicateSymbol:
    name: str       # contains(p1)
    var: Any        # BoolRef (obs_0)


# =====================================================
# Predicate Manager
# =====================================================


class PredicateManager:
    '''
    Maintains bijection:
        observer call <-> atomic boolean variable
    '''
    def __init__(self):
        self.pred_to_var: Dict[str, PredicateSymbol] = {}
        self.var_to_pred: Dict[str, str] = {}
        self.counter = 0


    def store_var(self, pred_str: str):
        '''
        Store the predicate string into PredicateManager 
        '''
        var_name = f'a{self.counter}'
        self.counter += 1
        solver_var = SOLVER.bool(var_name)
        ps = PredicateSymbol(pred_str, solver_var)
        self.pred_to_var[pred_str] = ps
        self.var_to_pred[str(solver_var)] = pred_str
    
    def get_var(self, pred_str: str):
        '''
        Get or create Boolean variables
        '''
        pred_str = pred_str.strip()
        if pred_str not in self.pred_to_var:
            self.store_var(pred_str)
        return self.pred_to_var[pred_str].var
    
    def predicate_key(self, pred: Predicate):
        return pred.to_string()
    
        # if pred.is_equality:
        #     return f"{pred.equality}"
        # return pred.to_string()


    

    def get_atom(self, pred: Predicate):
        key = self.predicate_key(pred)
        if key not in self.pred_to_var:
            self.store_var(key)
        return self.pred_to_var[key]
    

    def encode_expression(self, expr_text: str):
        ''' 
        Replace ALL occurrences of predicates with atomic variables

        Example:
        "(p1 == b0) && contains(b0)"
            →
        "(a0 && a1)
        '''

        text = expr_text

        # ----------------------------------------
        # STEP 1: Replace FULL equality predicates
        # e.g. size() == b0, p1 != b0
        # ----------------------------------------
        eq_pattern = r"[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?\s*(?:==|!=)\s*[A-Za-z_][A-Za-z0-9_]*"

        # full matches (needed because group returns partial)
        full_matches = re.findall(eq_pattern, text)

        for m in sorted(full_matches, key=len, reverse=True):
            var = self.get_var(m)
            text = re.sub(re.escape(m), str(var), text)
            return text

        # ----------------------------------------
        # STEP 2: Replace standalone observer calls
        # e.g. size(), contains(b0)
        # ----------------------------------------
        obs_pattern = r"\(?[A-Za-z_][A-Za-z0-9_]*\([^()]*\)\)?"

        obs_matches = re.findall(obs_pattern, text)

        for m in sorted(obs_matches, key=len, reverse=True):
            var = self.get_var(m)
            # text = re.sub(rf"{re.escape(m)}", str(var), text)
            text = re.sub(re.escape(m), str(var), text)
            return text

    
    def decode_expression(self, expr_str: str):
        
        result = expr_str

        for var, pred in self.var_to_pred.items():
            result = re.sub(rf"\b{re.escape(var)}\b", pred, result)

        return result

    

# global instance
PM = PredicateManager()



