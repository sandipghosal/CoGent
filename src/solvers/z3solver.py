from z3 import *
from solvers.interface import Solver
from common_imports import log



def is_atom(t):
    if not is_bool(t):
        return False
    if not is_app(t):
        return False
    k = t.decl().kind()
    if k == Z3_OP_AND or k == Z3_OP_OR or k == Z3_OP_IMPLIES:
        return False
    if k == Z3_OP_EQ and t.arg(0).is_bool():
        return False
    if k == Z3_OP_TRUE or k == Z3_OP_FALSE or k == Z3_OP_XOR or k == Z3_OP_NOT:
        return False
    return True


def atoms(fml):
    visited = set([])
    atms = set([])

    def atoms_rec(t, visited, atms):
        if t in visited:
            return
        visited |= {t}
        if is_atom(t):
            atms |= {t}
        for s in t.children():
            atoms_rec(s, visited, atms)

    atoms_rec(fml, visited, atms)
    return atms


def atom2literal(m, a):
    if is_true(m.eval(a)):
        return a
    return Not(a)


def implicant(atoms, s, snot):
    m = snot.model()
    lits = [atom2literal(m, a) for a in atoms]
    is_sat = s.check(lits)
    assert is_sat == unsat
    core = s.unsat_core()
    return Or([mk_not(c) for c in core])


def dnf_implicant(atoms, s, sfml):
    """
    Dual of `implicant`. Here `sfml` holds fml (supplies a satisfying
    model), and `s` holds Not(fml) (supplies the unsat core). The
    resulting core is a minimal conjunction of literals (a prime
    implicant term) that is sufficient to guarantee fml is true.
    """
    m = sfml.model()
    lits = [atom2literal(m, a) for a in atoms]
    is_sat = s.check(lits)
    assert is_sat == unsat
    core = s.unsat_core()
    if len(core) == 1:
        return core[0]
    return And([c for c in core])


class Z3Solver(Solver):
    def __init__(self):
        self._solver = z3.Solver()

    def int(self, id: str):
        return Int(id)
    
    def bool(self, id: str):
        return Bool(id)

    def bool_val(self, arg):
        return BoolVal(True) if arg == True else BoolVal(False)
    
    def int_val(self, arg):
        return IntVal(arg)
    
    def function(self, id, *args):
        return Function(id, *args)
    
    # def _or(self, a, b):
    #     '''
    #     Returns disjunction of a and b
    #     '''
    #     if not isinstance(a, z3.z3.BoolRef):
    #         a = self.bool(a)
    #     if not isinstance(b, z3.z3.BoolRef):
    #         b = self.bool(b)
    #     return simplify(Or(a, b))
    
    def _or(self, *args):
        '''
        Returns disjunction of a and b
        '''
        # if not isinstance(a, z3.z3.BoolRef):
        #     a = self.bool(a)
        # if not isinstance(b, z3.z3.BoolRef):
        #     b = self.bool(b)
        return simplify(Or(*args))
    
    def _and(self, *args):
        '''
        Returns conjunction of a and b
        '''
        return simplify(And(*args))
    
    def _neg(self, arg):
        '''
        Returns negation of the parameter
        '''
        return Not(arg)
    
    def _ne(self, a, b):
        return Not(a == b)
    
    def _eq(self, a, b):
        return a == b
    
    def _lt(self, a, b):
        return a < b
    
    def _gt(self, a, b):
        return a > b
    
    def _leq(self, a, b):
        return a <= b
    
    def _geq(self, a, b):
        return a >= b
    
    def implies(self, ant, cons):
        return simplify(Implies(ant, cons))
    
    def _add(self, a, b):
        return a + b
    
    def _sub(self, a, b):
        return a-b
    
    def _exists(self, vars, arg):
        return Exists(vars, arg)
    
    def for_all(self, vars, arg):
        return ForAll(vars, arg)

    def _sat(self):
        return sat
    
    def _unsat(self):
        return unsat
    

    def is_false(self, x):
        return is_false(x)

    def get_ast_id(self, x, y):
        return Z3_get_ast_id(x, y)

    def _wp(self, argv, args):
        return substitute(argv, args)
    
    def substitute(self, argv, args):
        return self._wp(argv, args)
    
    def _simplify(self, argv):
        if argv in (BoolVal(True), BoolVal(False)):
            return argv
        return simplify(argv)
    
    def solve(self, *args):
        # s = z3.Solver()
        for a in args:
            self._solver.add(a)
        return self._solver.check()
    
    def is_implies(self, a, b) -> bool:
        '''
        Check if a => b is true
        '''
        expr = self._and(a, self._neg(b))
        return self._solver.check(expr) == self._unsat()
    
    def canonicalize(self, expr):
        """
        Recursively canonicalize solver expression:
        - sort arguments of Or / And
        - keep everything else unchanged
        """
        if is_not(expr):
            inner = self.canonicalize(expr.children()[0])
            return self._neg(inner)
        
        if is_or(expr) or is_and(expr):
            children = [self.canonicalize(c) for c in expr.children()]

            # sort based on string representation (stable key)
            children_sorted = sorted(children, key=lambda x: str(x))

            if is_or(expr):
                return self._or(*children_sorted)
            else:
                return self._and(*children_sorted)
            
        if expr.num_args() > 0:
            new_children = [self.canonicalize(c) for c in expr.children()]
            return expr.decl()(*new_children)

        return expr




    def check_equivalence(self, a, b, mode=0) -> bool:
        '''
        check equality of two expressions semantically or structurally.
        when mode=0 check semantically, mode=1 check structurally
        default mode is 0
        '''
        if mode == 0:
            fm = self._ne(a, b)
            if self.solve(fm) == unsat:
                self._solver.reset()
                return True
            else:
                self._solver.reset()
                return False
        if mode == 1:
            return str(self._simplify(a)) == str(self._simplify(b))
            # return z3.eq(self._simplify(a), self._simplify(b))
        
    def check_sat(self, vars, ant, cons=None):
        # Do negation of the implication
        if cons is not None:
            expr = self._and(ant, self._neg(cons))
        else:
            expr = self._neg(ant)

        log.debug('Negation of implication: '+ self._str(expr))
        # Add exists parameters and registers
        if vars!=[]:
            expr = self._exists(vars, expr)
        log.debug('Final expression before checking SAT: '+ self._str(expr))
        # check the validity
        result = self.solve(expr)
        return result
    
    def eliminate(self, vars, args):
        t = Then(Tactic('qe'), Tactic('simplify'), Tactic('solve-eqs'))
        expr = self._exists(vars, args)
        log.debug('Strongest postcondition: '+ self._str(expr))
        expr = t(expr).as_expr()
        return expr

    def _str(self, argv):
        return obj_to_string(argv)
    
    def to_cnf(self, fml):
        atms = atoms(fml)
        s = z3.Solver()
        snot = z3.Solver()
        snot.add(Not(fml))
        s.add(fml)

        while sat == snot.check():
            clause = implicant(atms, s, snot)
            yield clause
            snot.add(clause)

    def to_dnf_terms(self, fml):
        '''
        Generator that yields DNF terms (And-of-literals) of fml,
        one at a time. Mirrors to_cnf, but with the roles of
        fml / Not(fml) swapped so each yielded piece is a
        conjunction (prime implicant) rather than a clause.
        '''
        atms = atoms(fml)
        s = z3.Solver()      # holds Not(fml) -> supplies unsat core
        sfml = z3.Solver()   # holds fml      -> supplies models to cover
        s.add(Not(fml))
        sfml.add(fml)
        while sat == sfml.check():
            term = dnf_implicant(atms, s, sfml)
            yield term
            sfml.add(Not(term))

    def to_dnf(self, fml):
        '''
        Converts fml into an equivalent Z3 expression in DNF
        (disjunction of conjunctions of literals).
        '''
        terms = list(self.to_dnf_terms(fml))
        if not terms:
            # fml is unsatisfiable
            return self.bool_val(False)
        dnf = terms[0]
        for t in terms[1:]:
            dnf = Or(dnf, t)
        return simplify(dnf)

    # def to_dnf(self, fml):
    #     clauses = self.to_cnf(fml)
    #     d_clauses = list()
    #     for c in clauses:
    #         disjunction = Or([literal if literal.decl().name() != 'Not' else Not(literal.arg(0)) for literal in c])
    #         d_clauses.append(disjunction)
    #     dnf = self.bool_val(False)
    #     for d in d_clauses:
    #         dnf = self._or(dnf, d)
    #     print(self._str(dnf))

    
    
    def pretty_print(self, expr, parent_prec=0):
        """
        Convert solver expression into readable infix logical form
        """


        # precedence levels
        PREC_OR = 1
        PREC_AND = 2
        PREC_NOT = 3

        # OR
        if is_or(expr):
            parts = [self.pretty_print(c, PREC_OR) for c in expr.children()]
            # s = " || ".join(f"({p})" for p in parts)
            # s = " || ".join(parts)
            formatted_parts = []
            for c, p in zip(expr.children(), parts):
                if is_and(c):
                    formatted_parts.append(f"({p})")
                else:
                    formatted_parts.append(p)
            s = " || ".join(formatted_parts)
            if parent_prec > PREC_OR:
                return f"({s})"
            return s

        # AND
        if is_and(expr):
            parts = []
            for c in expr.children():
                p = self.pretty_print(c, PREC_AND)

                if is_or(c):
                    parts.append(f"({p})")
                else:
                    parts.append(p)

            s = " && ".join(parts)

            if parent_prec > PREC_AND:
                return f"({s})"
            return s
    
        # NOT   
        if is_not(expr):
            inner_expr = expr.children()[0]
            inner = self.pretty_print(inner_expr, PREC_NOT)

            if inner_expr.decl().name() in ["=", "distinct"]:
                return f"!({inner})"

            if is_and(inner_expr) or is_or(inner_expr):
                return f"!({inner})"

            return f"!{inner}"

        # equality
        if expr.decl().name() == "=":
            lhs, rhs = expr.children()
            return f"{self.pretty_print(lhs)} == {self.pretty_print(rhs)}"

        # inequality
        if expr.decl().name() == "distinct":
            lhs, rhs = expr.children()
            return f"{self.pretty_print(lhs)} != {self.pretty_print(rhs)}"

        # constants / variables / function calls
        if expr.num_args() == 0:
            return str(expr)

        # fallback (general)
        args = [self.pretty_print(c) for c in expr.children()]
        return f"{expr.decl().name()}({', '.join(args)})"
