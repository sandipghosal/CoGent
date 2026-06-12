from common_imports import(
    copy, log
)

from .free_variable import FV
from constraintbuilder import LogicalExpression
from ramodel import OutputKind, DataType, Method
from conditionbuilder import ObserverPredicate, Postcondition, PM




def ensure_free_vars(num, typ):
    existing = FV.get_all()

    # create more if needed
    while len(existing) < num:
        FV.new(typ)
        existing = FV.get_all()

    return existing




def make_atomic_expr(pred_str: str) -> LogicalExpression:
    """
    Convert predicate string into atomic Expression using PredicateManager
    """
    atomic_str = PM.encode_expression(pred_str)
    return LogicalExpression(atomic_str)




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
        if len(obs.params) == 0 and obs.output_kind is not OutputKind.VALUE:
            observer = Method(
                name=obs.name,
                params=obs.params,
                output_kind=OutputKind.TRUE,
                output=True
            )
            pred = ObserverPredicate(observer)
            postconditions.append(Postcondition(pred,pred.to_expression()))
            neg_pred = pred.negate()
            postconditions.append(Postcondition(neg_pred, neg_pred.to_expression()))
        
        # CASE 2: Parameterized observers returning True/False
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
            pred = ObserverPredicate(observer)
            postconditions.append(Postcondition(pred,pred.to_expression()))
            neg_pred = pred.negate()
            postconditions.append(Postcondition(neg_pred, neg_pred.to_expression()))

        # CASE 3: Unparameterized observer returning Value
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
            pred = ObserverPredicate(
                observer=observer,
                op = '=='
            )
            postconditions.append(Postcondition(pred,pred.to_expression()))
            neg_pred = pred.negate()
            postconditions.append(Postcondition(neg_pred, neg_pred.to_expression()))
        
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
        log.debug(f"For observer {obs} corresponding postconditions are: {pred} and {neg_pred}")
    log.debug("\n")
    return postconditions


                