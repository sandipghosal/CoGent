import copy
import logging

from z3 import *
import constraintsolver.solver as SOLVER


def isequal(clause1, clause2):
    if sorted(list(str(clause1))) == sorted(list(str(clause2))):
        return True
    else:
        return False


def equalMUSes(first, second):
    """
    Check if two list of constraints are same
    :param first: list of constraints
    :param second: list of constraints
    :return: A Boolean value true or false
    """
    if len(first) != len(second):
        return False

    for i in range(len(first)):
        flag = False
        for j in range(len(second)):
            if isequal(first[i], second[j]):
                flag = True
                break
        if not flag:
            return False

    return True


def contains(mus, condition):
    """
    Check if a MUS contains a constraint 'condition'
    :param mus: a list of constraints
    :param condition: the condition of interest
    :return: Boolean value
    """
    for i in range(len(mus)):
        if isequal(mus[i], condition):
            return True
    return False


def get_unique_constraints(constraints):
    indices = list()
    for i in range(len(constraints) - 1):
        for j in range(i + 1, len(constraints)):
            if isequal(constraints[i], constraints[j]):
                indices.append(j)

    if indices:
        temp = list()
        for i in range(len(constraints)):
            if i not in indices:
                temp.append(constraints[i])
        # [temp.append(constraints[i]) for i in range(len(constraints)) if i not in indices]
        constraints = temp
    return constraints


def filter_subsets(subsets, condition):
    """
    Perform filtering:
    (a) Extract constraints other than a given condition 'cond' from a subset, e.g., if (c1^c2^cond) then extract (c1^c2)
    (b) Consider all those MUS that do not have 'cond' as a constraint

    Modified on 2023.04.24:
    Perform filtering:
    (a) First, consider all MUSes those contain the condition
    (b) Second, extract subsets from the MUSes from first step that contain only constraints other than the given condition
    :param subsets: list of all minimal unsatisfiable subsets (MUS) (list of lists)
    :param condition: weakest precondition (one of the possible clause in the MUS)
    :return: list of lists where each inner list must contain the condition
    """
    muses = list()
    for s in subsets:
        if contains(s, condition):
            muses.append(s)

    finalset = list()
    for s in muses:
        m = list()
        for i in range(len(s)):
            # Equivalence check using z3 not working when s[i] and condition
            # are coming from two different source
            # if SOLVER.equivalence(s[i], condition):
            # here is a hack using string comparison for comparing syntactically
            if not isequal(s[i], condition):
                m.append(s[i])
            # else:
            #     muses.append(s)
            #     break
        finalset.append(m)
    return finalset





def get_id(x):
    return Z3_get_ast_id(x.ctx.ref(), x.as_ast())


class SubsetSolver:
    # constraints = []
    # n = 0
    # s = Solver()
    # varcache = {}
    # idcache = {}

    def __init__(self, constraints):
        self.constraints = constraints
        self.n = len(constraints)
        self.s = Solver()
        self.varcache = {}
        self.idcache = {}
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
    muses = list()
    constraints = list(set(constraints + [condition]))
    constraints = get_unique_constraints(constraints)
    logging.debug('Final list of guards: ' + str(constraints))
    csolver = SubsetSolver(constraints)
    msolver = MapSolver(n=csolver.n)
    for orig, lits in enumerate_sets(csolver, msolver):
        output = "%s %s" % (orig, lits)
        logging.debug(output)
        if orig == 'MUS':
            muses.append(lits)
            # output = "%s %s" % (orig, lits)
            # logging.debug(output)
    return filter_subsets(muses, condition)
