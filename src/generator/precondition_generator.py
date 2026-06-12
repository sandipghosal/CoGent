from common_imports import(
    List, Any, Dict, Tuple, 
    field, copy, product, 
    permutations, log, SOLVER
)

from .free_variable import FV
from constraintbuilder import Expression
from conditionbuilder import (
    PM, Predicate, ObserverPredicate, EqualityPredicate, 
    BooleanPredicate, Precondition, Postcondition, Conjunct
)
from ramodel import (
    Automaton, OutputKind, Method, Location
)
from solvers import mus as MUS

methods_by_loc: Dict[str, List[Method]] = {}

def compute_observers_per_loc(A: Automaton, loc: Location):
    '''
    Prepare the list of observers in a given location
    '''
    for tr in A.trans_by_src_dst[(loc.name, loc.name)]:
        methods_by_loc.setdefault(loc.name, []).append(tr.input)


def substitute_params(loc: Location, Q: Postcondition) -> List[Method]:
    '''
    Prepare the list of observers in location loc by substituting the input parameters
    by free variables
    '''
    free_vars = FV.get_all()
    substituted_methods = []
    base_methods = methods_by_loc[loc.name]

    for m in base_methods:
        # CASE1: no parameters at all
        if not m.params and not m.output_params:
            substituted_methods.append(copy.deepcopy(m))
            continue

        # CASE2: input parameters
        if m.params:
            # generate all mappings: params -> free vars
            for combo in product(free_vars, repeat=len(m.params)):
                new_m = copy.deepcopy(m)
                subs = list(zip(m.params, combo))
                new_m.params = [copy.deepcopy(v) for v in combo]
                #substitute condition
                if new_m.condition:
                    sub_pairs = [
                        (p_old.to_solver_expr(), p_new.to_solver_expr())
                         for (p_old, p_new) in subs
                    ]
                    new_expr = SOLVER.substitute(
                        new_m.condition.solver_expr, sub_pairs
                    )

                    new_m.condition = Expression(str(new_expr), new_expr)
                substituted_methods.append(new_m)
            
        # CASE3: output parameters
        if m.output_params:
            for b in free_vars:
                new_m = copy.deepcopy(m)
                # assuming single output param
                new_m.output_params = [copy.deepcopy(b)]
                substituted_methods.append(new_m)

    return substituted_methods




def generate_equalities(target: Method, Q: Postcondition) -> List[Expression]:
    '''
    Generate constraints such as p1==b0, p1!=b0, b1==(b0+1), b0==(b1-1), etc.
    '''
    equalities: List[Expression] = []
    # CASE1: If the target and observer in postcondition both have input parameters 
    observer = Q.predicate.observer
    if len(target.params) > 0 and len(observer.params) > 0:
        target_params = [str(p) for p in target.params]
        postcdn_params = [str(p) for p in observer.params]
        for e in list(product(target_params, postcdn_params)):
            equalities.append(Expression(f"{e[0]}=={e[1]}"))
            equalities.append(Expression(f"{e[0]}!={e[1]}"))

    # CASE2: If observer in postcondition has output parameter
    if len(observer.params) == 0 and len(observer.output_params) > 0:
        free_vars = FV.get_all()
        for a, b in permutations(free_vars, 2):
            equalities.append(Expression(f"{a}==({b}+1)"))
            equalities.append(Expression(f"{a}==({b}-1)"))
    return equalities


def prepare_predicates(loc, equalities, Q) -> List[Predicate]:
    '''
    Prepare list of Predicate after substituting old parameter by new input parameters
    in the method condition
    '''

    free_vars = FV.get_all()
    base_methods = methods_by_loc[loc.name]
    candidates: List[Predicate] = list()

    def prepare_substitute_param(old_param) -> List[Tuple]:
        # generate all mappings: params -> free vars
        subs = []
        for combo in product(free_vars, repeat=len(old_param)):
            # subs = list(zip(old_param, combo))
            subs.extend(zip(old_param, combo))
        return subs

    def replace_input_params(method, subs) -> List[Method]:
        '''
        Return a list of methods each with input parameters replaced by the
        free variables
        '''
        new_methods = []
        for s in subs:
            m = copy.deepcopy(method)
            old, new = s
            subst = {old.name: new}
            m.params = [
                subst.get(p.name, p)
                for p in m.params
            ]
            new_methods.append(m)
            
        return new_methods

    def replace_output_params(method, subs) -> List[Method]:
        '''
        Return a list of methods each with output parameters replaced by the
        free variables
        '''
        new_methods = []
        for s in subs:
            m = copy.deepcopy(method)
            m.output_params = [s[1]]
            new_methods.append(m)
        return new_methods

    def replace_condition(methods, subs) -> None:
        for m in methods:
            if str(m.condition) not in ['True', 'False']:
                text_expr = str(m.condition)
                for old, new in subs:
                    for p in m.params:
                        if p.name == new.name:
                            text_expr = text_expr.replace(old.name, new.name)
                subs_expr = [(a.to_solver_expr(), b.to_solver_expr()) for (a, b) in subs]
                solver_expr = SOLVER.substitute(m.condition.solver_expr, subs_expr)
                m.condition = Expression(text_expr, solver_expr)

    for m in base_methods:
        # CASE1: no parameters at all
        if not m.params and not m.output_params:
            candidates.append(
                ObserverPredicate(observer=copy.deepcopy(m)) 
                if m.output_kind == OutputKind.TRUE
                else ObserverPredicate(observer=copy.deepcopy(m), negated=True) 
                )

        # CASE2: input parameters present
        if m.params and not m.output_params:
            # new_m = copy.deepcopy(m)
            subs = prepare_substitute_param(m.params)
            new_methods = replace_input_params(m, subs)
            replace_condition(new_methods, subs)
            for m in new_methods:
                candidates.append(
                    ObserverPredicate(observer=m) 
                    if m.output_kind == OutputKind.TRUE
                    else ObserverPredicate(observer=m, negated=True) 
                    )
        # CASE3: output parameters present
        if m.output_params:
            # new_m = copy.deepcopy(m)
            subs = prepare_substitute_param(m.output_params)
            new_methods = replace_output_params(m, subs)
            for new_m in new_methods:
                expr = Expression(f"{new_m.output_params[0]} == {new_m.output}")
                candidates.append(ObserverPredicate(observer=new_m, op='=='))
    for eq in equalities:
        candidates.append(EqualityPredicate(expr=eq))
    log.debug(
    "List of candidates for precondition: %s",
    ", ".join(f"{item}: {item.get_condition()}" for item in candidates)
    )
    return candidates

from typing import List


def remove_redundants(subsets: List[list]) -> List[list]:
    """
    Remove duplicate-equivalent subsets according to MUS.equalMUSes().
    """

    seen = set()
    unique = []
    for subset in subsets:
        key = frozenset(str(c) for c in subset)
        if key not in seen:
            seen.add(key)
            unique.append(subset)
    return unique

    # duplicate_indices = set()

    # for i, subset_i in enumerate(subsets[:-1]):
    #     for j, subset_j in enumerate(subsets[i + 1:], start=i + 1):
    #         if MUS.equalMUSes(subset_i, subset_j):
    #             duplicate_indices.add(j)

    # return [
    #     subset
    #     for idx, subset in enumerate(subsets)
    #     if idx not in duplicate_indices
    # ]

def conjunct_expr(subset):
    expr = SOLVER.bool_val(True)
    for c in subset:
        expr = SOLVER._and(expr, c)
    return expr

def remove_subsumed(subsets) -> List[list]:
    conjuncts = [conjunct_expr(s) for s in subsets]
    keep = [True] * len(subsets)
    for i in range(len(subsets)):
        for j in range(len(subsets)):
            if i == j or not keep[i]:
                continue
            # check if i is subsumed by j, i.e., S[j] -> S[i]
            if SOLVER.is_implies(conjuncts[j], conjuncts[i]):
                if len(subsets[j])<= len(subsets[i]):
                    keep[i] = False
                    break
    return [s for s, k in zip(subsets, keep) if k]

def refine(muses: List[list], condition) -> List[list]:
    """
    Apply refinement rules to generated MUSes.
    """
    muses =  remove_redundants(muses)
    muses = remove_subsumed(muses)
    return muses


def get_MUSes(antecedent, consequent):
    """
    Obtain all Minimal Unsatisfiable Subsets (MUSes).
    """
    muses = MUS.generate(antecedent, consequent)
    return [] if not muses else refine(muses, consequent)


def generate_precondition(A: Automaton, loc: Location, target: Method, wp: Expression, Q: Postcondition) -> List[Precondition]:
    '''
    Derive the precondition in location loc wrt. weakest precondition wp for 
    postcondition Q, and invariant in loc
    '''
    # if the location wise list of observers were not prepared earlier
    if loc.name not in methods_by_loc.keys():
        compute_observers_per_loc(A, loc)
    equalities = generate_equalities(target, Q)
    candidates = prepare_predicates(loc, equalities, Q)

    def replace_constants(solver_expr, subs):
        solver_expr_replaced = SOLVER.substitute(solver_expr, subs)
        return solver_expr_replaced
     
    def prepare_antecedent(candidates, subs)-> List[Any]:
        '''
        Prepare the antecedent as a list of solver expressions.
        Replace the constants in each expression by the corresponding constant value.
        Return the final list of substituted expressions. 
        '''
        solver_exprs = []
        for c in candidates:
            if subs:
                solver_exprs.append(replace_constants(c.get_condition().solver_expr, subs))
            else:
                solver_exprs.append(c.get_condition(), subs)
        # log.debug('Final list of candidates for precondition: %s',
        # ', '.join(str(e) for e in solver_exprs)
        # )
        return solver_exprs
    
    def prepare_consequent(invariant, wp, subs):
        '''
        Prepare consequent as a solver expression of ~(Inv->WP)
        Then substitute the constants and return the final expression
        '''
        clause = SOLVER._neg(
        SOLVER.implies(
            invariant.solver_expr,
            wp.solver_expr
            )
        )
        ante_expr = replace_constants(clause, subs) if subs else clause
        log.debug(f"~(Inv->WP): {ante_expr}")
        return ante_expr


    def match_expr_to_predicate(expr, candidates):
        for pred in candidates:
            if SOLVER.check_equivalence(
                pred.get_condition().solver_expr,
                expr,
                mode=1
            ):
                return pred
            
    def add_truth_predicates():
        '''
        Add location wise truth predicates.
        E.g., add the predicates isempty() and !isfull() for location l0
        '''
        new_predicates = []
        for method in A.location_truth_predicates[loc.name]:
            pred = None
            if method.output_kind == OutputKind.TRUE:
                pred = ObserverPredicate(observer=method)
            elif method.output_kind == OutputKind.FALSE:
                pred = ObserverPredicate(observer=method, negated=True)
            else:
                continue
            new_predicates.append(pred)
        return new_predicates
    
        # if len(predicates) == 1:
        #     if predicates[0].to_string() == 'True':
        #         for method in A.location_truth_predicates[loc.name]:
        #             # only consider isempty() or isfull() and not size()
        #             if method.output_kind in [OutputKind.TRUE, OutputKind.FALSE]:
        #                 new_predicates.append(ObserverPredicate(observer=method))
        # else:
        #     new_predicates = predicates
        #     for method in A.location_truth_predicates[loc.name]:
        #             # only consider isempty() or isfull() and not size()
        #             if method.output_kind in [OutputKind.TRUE, OutputKind.FALSE]:
        #                 new_predicates.append(ObserverPredicate(observer=method))
        # return new_predicates
            
    def create_preconditions(conjuncts_list) -> Precondition:
        conjunts: List[Precondition] = []

        # if the set of constraints is blank then
        # we can add a contract like {False} push(p1) {Q}
        if not conjuncts_list or conjuncts_list == [[]]:
            predicates: List[Predicate] =[]
            # predicates.append(
            #     BooleanPredicate(Expression('False'))
            #     if wp.text == 'False'
            #     else BooleanPredicate(Expression('True'))
            # )
            if wp.text == 'True':
                predicates.append(BooleanPredicate(Expression('True')))
                predicates = add_truth_predicates()
                return Precondition([Conjunct(predicates)])
            else:
                # No precondition created if weakest precondition is not True
                return None
        else:
            for c_list in conjuncts_list:
                predicates: List[Predicate] = []
                for expr in c_list:
                    pred = match_expr_to_predicate(expr, candidates)
                    predicates.append(pred)
                conjunts.append(Conjunct(predicates))
            new_predicates = add_truth_predicates()
            conjunts.append(Conjunct(new_predicates))
            return Precondition(conjunts)

    # prepare list of (const, value) tuples for substitution
    const_subs = []
    for c in A.constants.consts.values():
            const_subs.append((c.to_solver_expr(), SOLVER.int_val(c.value)))
    ante = prepare_antecedent(candidates, const_subs)
    cons = prepare_consequent(loc.invariant, wp, const_subs)

    mus_lists = get_MUSes(ante, cons)
    log.debug(
        'MUSes after excluding ~(Inv->WP): %s',
        ', '.join(str(s) for s in mus_lists)
    )

    return create_preconditions(mus_lists)
    # return None

    
    
    # conjuncts = []
    # for candidate_set  in generated_candidates:
    #     preds = []
    #     for item in candidate_set:
    #         if isinstance(item, Method):
    #             preds.append(Predicate(observer=item))
    #         else:
    #             preds.append(Predicate(equality=item))
    #     conjuncts.append(Conjunct(preds))

    # return Precondition(conjuncts)
    


    
    

    