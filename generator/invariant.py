import logging
import re

import z3.z3

import smtsolvers.solver as S
import ramodel.automaton as RA
import constraintbuilder.build_expression as BE

automaton = None

# define a dictionary of the form {location1 : {set of locations depends on location1}}
dependent = dict()


def parents_of_location(loc) -> list:
    """
    Returns the list of parent location for a given location
    :param loc: a Location object
    :return: a list of locations identified as the parent of input location
    """
    global dependent
    parents = list()
    for k, v in dependent.items():
        if loc in v:
            parents.append(k)
    return parents


def replace_in_expr(expr) -> (set, z3.z3.BoolRef):
    """
    Replace each register variable in the expression with a new variable
    and return the new expression with the set of new variables those have
    replaced the old ones
    :param expr: BoolRef object
    :return: set of new variables, expression after substitution

    >>> expr = And(r1 == p, r2 == p)
    >>> replace_in_expr(expr)
    {r1', r2'}, And(r1' == p, r2' == p)
    """
    list_subs = set()
    oldvars = set()
    vars = set(re.findall(r'\b[pr][0-9]+', str(expr)))
    for v in vars:
        if v.find('r') != -1:
            v_old = S._int(v + '\'')
            list_subs.add((S._int(v), v_old))
        if v.find('p') != -1:
            v_old = S._int(v)
        oldvars.add(v_old)
    return oldvars, S.do_substitute(expr, list_subs)


def replace_in_assignment(expr, registers) -> (set, z3.z3.BoolRef):
    """
    Replace registers and parameters in the rhs of the assignment by new variables
    and return the new expression with the set of new variables those have
    replaced the old ones
    :param expr: list of pairs in the form (lhs, rhs)
    :param registers: list of registers
    :return: set of new variables, expression formed after substitution

    >>> expr = [(r2, r1), (r1, p)]
    >>> registers = [r1, r2]
    >>> replace_in_assignment(expr, registers)
    {r1', p}, And(r2 == r1', r1 == p)
    >>> expr = []
    >>> registers = [r1, r2]
    >>> replace_in_assignment(expr, registers)
    >>> {r1', r2'}, And(r1 == r1', r2 == r2')
    """
    newexpr = S._boolval(True)
    # set of variables that would be quantified
    oldvars = set()
    # foreach tuple (assignment) replace the old register variable in rhs by a new variable

    # prepare a list of registers in the lhs of all the assignments
    lhs = list()
    for item in expr:
        if re.match(r'r[0-9]+', str(item[0])):
            lhs.append(item[0])

    # add the missing assignments explicitly
    for r in list(set(registers) - set(lhs)):
        expr.append((r, r))

    for item in expr:
        if re.match(r'r[0-9]+', str(item[0])) is None:
            continue
        if re.search('[r]', str(item[1])):
            var = S._int(str(item[1]) + '\'')
            oldvars.add(var)
            newexpr = S._and(newexpr, S._eq(item[0], var))
        if re.search('[p]', str(item[1])):
            oldvars.add(item[1])
            newexpr = S._and(newexpr, S._eq(item[0], item[1]))

    return oldvars, newexpr


def replace_old(expr, registers) -> None:
    if isinstance(expr, z3.z3.BoolRef):
        # Uncomment for testing
        # expr = BE.build_expr("(r1 == p) && (r2 == p)")
        if str(expr) in ['True', 'False']:
            return {}, expr
        else:
            vars, expr = replace_in_expr(expr)
            return vars, expr
    elif isinstance(expr, list):
        vars, expr = replace_in_assignment(expr, registers)
        return vars, expr


def get_postcondition(source, dest, pre_registers, guard, assignments) -> z3.BoolRef:
    """
    Derive strongest postcondition for the destination location wrt. given source location, guard and the assignments
    :param source: source location (Location)
    :param dest: destination location (Location)
    :param pre_registers: list of resgieters for source location
    :param guard: guard of the transition (BoolRef)
    :param assignments: list of assignments (Tuples)
    :return:
    """
    global automaton
    precondition = None

    # The precondition for the initial location is True
    if source.invariant is None:
        source.invariant = S._boolval(True)

    precondition = source.invariant

    logging.debug('Precondition: ' + str(precondition))
    logging.debug('Guard: ' + str(guard))
    logging.debug('Assignment: ' + str(assignments))

    set1, a_expr = replace_old(assignments, pre_registers)
    set2, p_expr = replace_old(precondition, pre_registers)
    set3, g_expr = replace_old(guard, pre_registers)

    oldvars = list(set1.union(set2, set3))

    expr = S._boolval(True)
    for e in [a_expr, g_expr, p_expr]:
        expr = S._and(expr, e)

    if str(expr) not in ['True', 'False']:
        postcondition = S.eliminate(oldvars, expr)
    else:
        postcondition = expr

    logging.debug('Postcondition after quantifier elimination: ' + str(postcondition))

    return postcondition

    # # assign the derived postcondition as local invariant
    # if dest.invariant is None:
    #     dest.invariant = postcondition
    #     logging.debug('Postcondition has changed')
    #     return True
    # else:
    #     # if the destination location has more than one parent location then
    #     # the new postcondition shall be and of old and new postcondition
    #     if len(parents_of_location(dest)) > 1:
    #         old_expr = dest.invariant
    #         dest.invariant = S._and(dest.invariant, postcondition)
    #         if str(old_expr) != str(dest.invariant):
    #             logging.debug('Postcondition has changed')
    #             return True
    #         else:
    #             return False
    #     else:
    #         if str(dest.invariant) != str(postcondition):
    #             dest.invariant = postcondition
    #             return True
    #         else:
    #             return False


def new_postcondition(source, dest, pre_registers, guard, assignments) -> bool:
    postcondition = get_postcondition(source, dest, pre_registers, guard, assignments)
    if dest.invariant != postcondition:
        pass
    return True


def get_transition(source, dest) -> RA.Transition:
    """
    Get the transition between the source and destination locations caused by the target method
    :param source: the location whose invariant is used for precondition
    :param dest: the location whose invarinat shall be derived as the postcondition
    :return: an object of class Transition
    """
    global automaton
    logging.debug('\nSource: ' + str(source) + ', Destination: ' + str(dest))
    transitions = source.get_transitions(destination=dest)
    logging.debug(str(transitions))
    return transitions


def derive_sp(source, dest, registers, transitions) -> bool:

    sp = S._boolval(False)

    for tran in transitions:
        sp = S._or(sp, get_postcondition(source, dest, registers, tran.method.guard, tran.assignments))

    logging.debug('Final postcondition: ' + str(sp))

    # assign the derived postcondition as local invariant
    if dest.invariant is None:
        dest.invariant = sp
        logging.debug('Postcondition has changed')
        return True
    else:
        # if the destination location has more than one parent location then
        # the new postcondition shall be OR of old and new postcondition
        if len(parents_of_location(dest)) > 1:
            old_expr = dest.invariant
            dest.invariant = S._or(dest.invariant, sp)
            if str(old_expr) != str(dest.invariant):
                logging.debug('Postcondition has changed')
                return True
            else:
                return False
        else:
            if str(dest.invariant) != str(sp):
                dest.invariant = sp
                return True
            else:
                return False


def generate(x):
    global dependent
    # if the location x has child locations
    if x in dependent.keys():
        # foreach child location derive the strongest postcondition
        for y in dependent[x]:
            if x == y:
                continue
            transitions = get_transition(x, y)
            logging.debug('Derive postcondition for ' + str(y))
            logging.debug('Registers in location ' + str(y) + ': ' + str(y.registers))

            changed = derive_sp(x, y, y.registers, transitions)

            # if the postcondition of y has been changed from earlier
            # then evaluate the postcondition for the children of y
            if changed:
                generate(y)


def bfs(startloc):
    global dependent

    # apply BFS algorithm to find all reachable states wrt. the target method
    visited = []
    queue = []

    queue.append(startloc)

    while queue:
        location = queue.pop(0)
        visited.append(location)
        dependent[location] = set()

        # if the destination location is not visited
        for dest in location.get_destinations():
            dependent[location].add(dest)
            if dest not in visited:
                queue.append(dest)


def generate_invariants(config) -> None:
    """
    Function generates local invariant for each of the location in the automaton starting from initial location
    :param start_location: a Location object denoting the starting location
    :return:
    """
    global automaton
    automaton = config

    # populate the dependent dictionary using BFS approach
    bfs(automaton.START_LOCATION)

    logging.debug('Dependency graph: ' + str(dependent))
    # start generating strongest postcondition calling the recursive function generate
    generate(automaton.START_LOCATION)
    # exit(0)
    return
