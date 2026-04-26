from z3 import *
import smtsolvers.solver as SOLVER


def filter_subsets(subsets, condition):
    """ Filter out subset based on the presence of wp condition """
    muses = list()
    for s in subsets:
        flag = False
        for i in range(len(s)):
            if SOLVER.equivalence(s[i], condition):
                flag = True
                break
        if flag: muses.append(s)

    return muses


def get_id(x):
    return Z3_get_ast_id(x.ctx.ref(), x.as_ast())


class SubsetSolver:
    constraints = []
    n = 0
    s = Solver()
    varcache = {}
    idcache = {}

    def __init__(self, constraints):
        self.constraints = constraints
        self.n = len(constraints)
        for i in range(self.n):
            self.s.add(Implies(self.c_var(i), constraints[i]))

    def c_var(self, i):
        if i not in self.varcache:
            v = Bool(str(self.constraints[abs(i)]))
            self.idcache[get_id(v)] = abs(i)
            if i >= 0:
                self.varcache[i] = v
            else:
                self.varcache[i] = Not(v)
        return self.varcache[i]

    def check_subset(self, seed):
        assumptions = self.to_c_lits(seed)
        return (self.s.check(assumptions) == sat)

    def to_c_lits(self, seed):
        return [self.c_var(i) for i in seed]

    def complement(self, aset):
        return set(range(self.n)).difference(aset)

    def seed_from_core(self):
        core = self.s.unsat_core()
        return [self.idcache[get_id(x)] for x in core]

    def shrink(self, seed):
        current = set(seed)
        for i in seed:
            if i not in current:
                continue
            current.remove(i)
            if not self.check_subset(current):
                current = set(self.seed_from_core())
            else:
                current.add(i)
        return current

    def grow(self, seed):
        current = seed
        for i in self.complement(current):
            current.append(i)
            if not self.check_subset(current):
                current.pop()
        return current


class MapSolver:
    def __init__(self, n):
        """Initialization.
              Args:
             n: The number of constraints to map.
        """
        self.solver = Solver()
        self.n = n
        self.all_n = set(range(n))  # used in complement fairly frequently

    def next_seed(self):
        """Get the seed from the current model, if there is one.
             Returns:
             A seed as an array of 0-based constraint indexes.
        """
        if self.solver.check() == unsat:
            return None
        seed = self.all_n.copy()  # default to all True for "high bias"
        model = self.solver.model()
        for x in model:
            if is_false(model[x]):
                seed.remove(int(x.name()))
        return list(seed)

    def complement(self, aset):
        """Return the complement of a given set w.r.t. the set of mapped constraints."""
        return self.all_n.difference(aset)

    def block_down(self, frompoint):
        """Block down from a given set."""
        comp = self.complement(frompoint)
        self.solver.add(Or([Bool(str(i)) for i in comp]))

    def block_up(self, frompoint):
        """Block up from a given set."""
        self.solver.add(Or([Not(Bool(str(i))) for i in frompoint]))


def enumerate_sets(csolver, map):
    """Basic MUS/MCS enumeration, as a simple example."""
    while True:
        seed = map.next_seed()
        if seed is None:
            return
        if csolver.check_subset(seed):
            MSS = csolver.grow(seed)
            yield ("MSS", csolver.to_c_lits(MSS))
            map.block_down(MSS)
        else:
            seed = csolver.seed_from_core()
            MUS = csolver.shrink(seed)
            yield ("MUS", csolver.to_c_lits(MUS))
            map.block_up(MUS)


def generate(constraints, condition):
    mus = list()
    constraints = constraints + [condition]
    csolver = SubsetSolver(constraints)
    msolver = MapSolver(n=csolver.n)
    for orig, lits in enumerate_sets(csolver, msolver):
        if orig == 'MUS':
            mus.append(lits)
    return filter_subsets(mus, condition)


import smtsolvers.blalgebra as SYM

SYM.count_vars('(a0 or a1) and a2 and a1 and (a3 or a5)')