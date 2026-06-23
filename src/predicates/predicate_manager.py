from common_imports import(
    dataclass, Dict, re, SOLVER
)

from .predicate import Predicate


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
            # return text

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
            # return text
        return text
    
    def decode_expression(self, expr_str: str):
        
        result = expr_str

        for var, pred in self.var_to_pred.items():
            result = re.sub(rf"\b{re.escape(var)}\b", pred, result)

        return result

    

# global instance
PM = PredicateManager()



