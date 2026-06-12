from common_imports import(
    copy, Dict, List, log, SOLVER
)

from ramodel import Automaton, OutputKind, Method
from constraintbuilder import Expression
from conditionbuilder import (
    Contract, Precondition, 
    Postcondition, PM
)

from .precondition_generator import generate_precondition


def get_dest_observer(A: Automaton, tr, Q: Postcondition) -> Method:
    obs = Q.predicate.observer
    transitions = A.outgoing_for_input(tr.dest.name, obs.name)
    o: Method = None
    # get the input that matches with the return kind (True/False/Value)
    for tran in transitions:
        if tran.input.output_kind == obs.output_kind:
            o = copy.deepcopy(tran.input)
    # if there is no match create a dummy observer with desired return value
    # then set the condition to False
    if o is None:
        log.debug(f'No transition for {obs.name}=={obs.output} found in destination {tr.dest.name}')
        o = copy.deepcopy(obs)
        o.condition = Expression('False')
        log.debug(f"Created a dummy observer {o}=={obs.output} with condition {str(o.condition)} in location {tr.dest}")
    # if the observer returning a value, change the condition
    # to an equality relation, e.g., for size() that returns c1
    # set the condition to c1==b0 or c1!=b0 [];'
    if o.output_kind is OutputKind.VALUE:
        o.condition = (
            Expression(f"{o.output}=={obs.output_params[0]}") 
            if not Q.predicate.negated 
            else Expression(f"{o.output}!={obs.output_params[0]}") 
        )
    return o

def substitute_params(obs: Method, dest_obs: Method) -> Expression:
    sub = list(zip(dest_obs.params, obs.params))
    args = []
    for v in sub:
        args.append((v[0].to_solver_expr(), v[1].to_solver_expr()))
    g = SOLVER.substitute(dest_obs.condition.solver_expr, args)
    return Expression(str(g), g)

def substitute_wrt_assignment(g, tr) -> Expression:
    args = []
    for asn in tr.assignments:
        args.append((SOLVER.int(asn.target_reg), SOLVER.int(asn.expr)))
    g = SOLVER.substitute(g.solver_expr, args)
    return Expression(str(g), g)

def disjunction_of_transition_guards(tr_guards):
    result = SOLVER.bool_val(False)
    for g in tr_guards:
        result = SOLVER._or(result, g.solver_expr)
    return result

def conjunction_of_implications(implications):
    result = SOLVER.bool_val(True)
    for t in implications:
        result = SOLVER._and(result, SOLVER.implies(t[0], t[1]))
    return result

def derive_wp(A, loc, method, Q) -> Expression:
    '''
    Derive weakest precondition for location l, for the method m and
    postcondition Q
    '''
    pass
    tr_guards = []
    implications = []

    transitions = A.outgoing_for_input(loc.name, method.name)

    if not transitions:
        return None

    for tr in transitions:
        # get the guard of observer method in the destination of tr
        dest_obs = get_dest_observer(A, tr, Q)
        obs = Q.predicate.observer
        # substitute guard with the parameter of observer
        g = substitute_params(obs, dest_obs)
        g = substitute_wrt_assignment(g, tr)
        implications.append((tr.input.condition.solver_expr, g.solver_expr))
        tr_guards.append(tr.input.condition)

    g_disj = disjunction_of_transition_guards(tr_guards)
    g_conj = conjunction_of_implications(implications)
    final_wp = SOLVER._and(g_disj, g_conj)
    return Expression(str(final_wp), final_wp)




def derive_precondition(A, loc, method, Q) -> Precondition:
    wp_expr = derive_wp(A, loc, method, Q)
    log.debug(f"Weakest precondition(WP) in {loc}: {wp_expr}")
    log.debug(f"Invariant (Inv) in {loc}: {loc.invariant}")
    precond = generate_precondition(A, loc, method, wp_expr, Q)
    # return pre_expr
    return precond

def generate_contract_per_location(A: Automaton, target: Method, Q: Postcondition):
    '''
    Returns:
        Dict[location_name -> List[Contract]]
    '''
    contracts_per_location: Dict[str, List[Contract]] = {}
    for loc in A.locations.values():
        log.debug("\n")
        log.debug(f"Generate contract for location: {"\033[31m"}{loc}{"\033[36m"}")
        log.debug(f"Postcondition: {"\033[31m"}{Q}{"\033[36m"}")
        P = derive_precondition(A, loc, target, Q)
        if P is None:
            continue
        C = Contract(
            pre=P,
            method=target,
            post=Q
        )
        contracts_per_location.setdefault(loc.name, []).append(C)
        loc.contracts.append(C)
    return contracts_per_location
