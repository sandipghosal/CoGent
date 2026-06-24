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
# Shared building blocks (module-level, reused in both steps)
# =====================================================


IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
CALL       = rf"{IDENTIFIER}\([^()]*\)"          # name(args)  – no outer parens
OPERAND    = rf"(?:{CALL}|{IDENTIFIER})"


# Arithmetic term: stops at logical operators && || ! and unmatched )
# Only digits allowed after arithmetic operator (e.g. b1+1, b0-2)
# NOT another identifier, to avoid consuming && operands
ARITH_TERM  = rf"(?:{OPERAND}\s*[+\-*/]\s*\d+)"   # b1+1, b0-2, size()*2
ARITH_RHS   = rf"(?:{ARITH_TERM}|{OPERAND})"       # b1+1  OR just  b1

EQ_PATTERN  = (
    rf"(?P<lhs>{OPERAND})"                          # LHS: call or identifier
    rf"\s*(?P<op>==|!=)\s*"                         # operator
    rf"\(?"                                         # optional ( around RHS
    rf"(?P<rhs>{ARITH_RHS})"                        # RHS: arithmetic or plain
    rf"\)?"                                         # optional ) around RHS
)


OBS_PATTERN = (
    rf"(?<!\w)"                                  # not preceded by word char
    rf"(?P<call>{CALL})"                         # bare call – NO optional parens
)
# ─────────────────────────────────────────────────────────────────────────── #


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
    

    def _normalize(self, raw: str) -> str:
        """
        Strip surrounding whitespace and redundant outer parentheses
        so that  (I_isfull())  and  I_isfull()  map to the same key.
        """
        s = raw.strip()
        # repeatedly strip a single matching outer paren pair
        while s.startswith("(") and s.endswith(")"):
            # make sure the opening ( matches the closing )
            depth = 0
            for i, ch in enumerate(s):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                if depth == 0:
                    if i == len(s) - 1:
                        s = s[1:-1].strip()   # safe to strip
                    break                     # outermost ) closed early – stop
        return s



    def encode_expression(self, expr_text: str):
        ''' 
        Replace ALL occurrences of predicates with atomic variables.

        Examples
        --------
        "(p1 == b0) && contains(b0)"          →  "(a0 && a1)"
        "!(!(I_isfull()) && I_isempty()) || ((p1 == b0))"
                                               →  "(!(!a1 && a2) || a0)"
        "(b0 == b1 + 1)"                       →  "(a3)"
        '''

        text = expr_text

        # ----------------------------------------
        # STEP 1: Replace FULL equality predicates
        # e.g. size() == b0, p1 != b0
        # ----------------------------------------
        # eq_pattern = r"[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?\s*(?:==|!=)\s*[A-Za-z_][A-Za-z0-9_]*"
        
        eq_pattern = r"""
            [A-Za-z_][A-Za-z0-9_]*(?:\([^()]*\))?   # LHS
            \s*
            (?:==|!=)
            \s*
            (
                \(
                [A-Za-z0-9_]+
                (?:\s*[+\-*/]\s*[A-Za-z0-9_]+)+
                \)
                |
                [A-Za-z0-9_]+
            )
        """
        matches = [m.group() for m in re.finditer(eq_pattern, text, re.VERBOSE)]

        for m in sorted(matches, key=len, reverse=True):
            var = self.get_var(f"({m})")
            text = re.sub(re.escape(m), str(var), text)

        # ----------------------------------------
        # STEP 2: Replace standalone observer calls
        # e.g. size(), contains(b0)
        # ----------------------------------------

        # obs_pattern = r"\(?[A-Za-z_][A-Za-z0-9_]*\([^()]*\)\)?"

        # obs_matches = re.findall(obs_pattern, text)

        # for m in sorted(obs_matches, key=len, reverse=True):
        #     var = self.get_var(m)
        #     # text = re.sub(rf"{re.escape(m)}", str(var), text)
        #     text = re.sub(re.escape(m), str(var), text)

        obs_matches = [m.group("call") for m in re.finditer(OBS_PATTERN, text)]
        for m in sorted(obs_matches, key=len, reverse=True):
            var = self.get_var(self._normalize(m))
            text = re.sub(re.escape(m), str(var), text)
            
        return text
    
    def decode_expression(self, expr_str: str):
        
        result = expr_str

        for var, pred in self.var_to_pred.items():
            result = re.sub(rf"\b{re.escape(var)}\b", pred, result)

        return result

    

# global instance
PM = PredicateManager()



