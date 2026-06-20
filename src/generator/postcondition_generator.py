from common_imports import(
    copy, log
)

from .free_variable import FV

from conditions import Postcondition

from ramodel import (
    OutputKind, DataType, Method
)

from predicates import (
    BooleanObserverPredicate, 
    RelationalPredicate
)

from conditions import (
    Atom
)




def ensure_free_vars(num, typ):
    existing = FV.get_all()

    # create more if needed
    while len(existing) < num:
        FV.new(typ)
        existing = FV.get_all()

    return existing




# def make_atomic_expr(pred_str: str) -> LogicalExpression:
#     """
#     Convert predicate string into atomic Expression using PredicateManager
#     """
#     atomic_str = PM.encode_expression(pred_str)
#     return LogicalExpression(atomic_str)




def generate_postconditions(A):

    postconditions = []

    # ----------------------------------------
    # Create free variables ONCE
    # ----------------------------------------
    NUM_FREE_VARS = 2  # configurable

    free_vars = ensure_free_vars(NUM_FREE_VARS, DataType.INT)
    log.debug(f"List of free variables: {', '.join(str(v) for v in free_vars)}")

    # free_var_names = [v.name for v in free_vars]

    # ----------------------------------------
    # Iterate over observers
    # ----------------------------------------
    for obs in A.observers.values():
        # CASE 1: Unparameterized observers returning True/False
        # Examples: isempty(), isfull()
        if len(obs.params) == 0 and obs.output_kind is not OutputKind.VALUE:
            observer = Method(
                name=obs.name,
                params=obs.params,
                output_kind=OutputKind.TRUE,
                output=True
            )
            pred = BooleanObserverPredicate(observer)
            atom = Atom(pred)
            postconditions.append(Postcondition(atom))
            neg_pred = pred.negate()
            neg_atom = Atom(neg_pred)
            postconditions.append(Postcondition(neg_atom))
        
        # CASE 2: Parameterized observers returning True/False
        # Example: contains(p1)
        elif len(obs.params) > 0 and obs.output_kind is not OutputKind.VALUE:
            params = []
            i = 0
            for b in free_vars:
                if i==len(obs.params): break
                params.append(copy.deepcopy(b))
                i = i+1

            observer = Method(
                name=obs.name,
                params=params,
                output_kind=OutputKind.TRUE,
                output=True
            )

            pred = BooleanObserverPredicate(observer)
            atom = Atom(pred)
            postconditions.append(Postcondition(atom))
            neg_pred = pred.negate()
            neg_atom = Atom(neg_pred)
            postconditions.append(Postcondition(neg_atom))

        # CASE 3: Unparameterized observer returning Value
        # Example: size()
        elif len(obs.params) == 0 and obs.output_kind is OutputKind.VALUE:
            # considering only one output parameter
            out_params = []
            for b in free_vars:
                out_params.append(copy.deepcopy(b))
                break

            observer = Method(
                name=obs.name,
                params=obs.params,
                output_params=out_params,
                output_kind=OutputKind.VALUE
            )
            pred = RelationalPredicate(
                lhs = observer,
                op="==",
                rhs=observer.output_params[0]
            )
            atom = Atom(pred)
            postconditions.append(Postcondition(atom))

            neg_pred = pred.negate()
            neg_atom = Atom(neg_pred)
            postconditions.append(Postcondition(neg_atom))
        
        # CASE 4: Parameterized observer returning Value
        # elif len(obs.params) > 0 and obs.output_kind is OutputKind.VALUE:
        #     params = []
        #     i = 0
        #     for b in free_vars:
        #         if i==len(obs.params): break
        #         params.append(copy.deepcopy(b))
        #         i=i+1

        #     # considering only one output parameter 
        #     out_params = []
        #     for b in free_vars:
        #         out_params.append(copy.deepcopy(b))
        #         break
        #     observer = Method(
        #         name=obs.name,
        #         params=params,
        #         output_kind=OutputKind.VALUE
        #     )
        #     pred = ObserverPredicate(
        #         observer=observer,
        #         op = '==',
        #         output_params=out_params
        #     )
        #     postconditions.append(Postcondition(pred,pred.to_expression()))
        #     neg_pred = pred.negate()
        #     postconditions.append(Postcondition(neg_pred, neg_pred.to_expression()))
        log.debug(f"For observer {obs} corresponding postconditions are: {atom} and {neg_atom}")
    log.debug("\n")
    return postconditions


                