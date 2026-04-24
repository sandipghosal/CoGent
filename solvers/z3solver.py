from z3 import *
from solvers.interface import Solver


from customlogger import getlogger
log = getlogger(__name__)



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
    
    def _or(self, a, b):
        '''
        Returns disjunction of a and b
        '''
        if not isinstance(a, z3.z3.BoolRef):
            a = self.bool(a)
        if not isinstance(b, z3.z3.BoolRef):
            b = self.bool(b)
        return simplify(Or(a, b))
    
    def _and(self, a, b):
        '''
        Returns conjunction of a and b
        '''
        return simplify(And(a, b))
    
    def _neg(self, arg):
        '''
        Returns negation of the parameter
        '''
        return simplify(Not(arg))
    
    def _ne(self, a, b):
        return simplify(Not(a == b))
    
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

    def _wp(self, argv, args):
        return simplify(substitute(argv, args))
    
    def substitute(self, argv, args):
        return self._wp(argv, args)
    
    def _simplify(self, argv):
        if argv in (BoolVal(True), BoolVal(False)):
            return argv
        return simplify(argv)
    
    def solve(self, *args):
        s = Solver()
        for a in args:
            s.add(a)
        return s.check()

    def check_equivalence(self, a, b) -> bool:
        fm = (a != b)
        if self.solve(fm) == unsat:
            return True
        else:
            return False
        
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
    
    def to_cnf(fml):
        atms = atoms(fml)
        s = z3.Solver()
        snot = z3.Solver()
        snot.add(Not(fml))
        s.add(fml)

        while sat == snot.check():
            clause = implicant(atms, s, snot)
            yield clause
            snot.add(clause)


    def to_dnf(fml):
        clauses = self.to_cnf(fml)
        d_clauses = list()
        for c in clauses:
            disjunction = Or([literal if literal.decl().name() != 'Not' else Not(literal.arg(0)) for literal in c])
            d_clauses.append(disjunction)
        dnf = self.bool_val(False)
        for d in d_clauses:
            dnf = self._or(dnf, d)
        print(self._str(dnf))
    









