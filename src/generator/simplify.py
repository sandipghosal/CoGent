from common_imports import defaultdict, log, SOLVER, re
from sympy.logic.boolalg import to_dnf
from expressions import LogicalExpression
from predicates import PM


# =====================================================
# Build Conjunction
# =====================================================
def build_conjunction(preconditions):
    '''
    Build conjunction of all preconditions
    '''
    encoded_parts = []

    for pre in preconditions:
        s = str(pre).strip()
        if s == "None":
            continue

        if s == "True":
            continue

        if s == "False":
            return "False"
        
        encoded = PM.encode_expression(s)
        encoded_parts.append(f"({encoded})")
    
    # if not encoded_parts:
    #     return "True"

    expr_str = " && ".join(encoded_parts)
    log.debug("Encoded expression:")
    log.debug(expr_str)
    return expr_str



# =====================================================
# Simplify + DNF
# =====================================================
# def to_dnf(expr):
#     '''
#     Try solver DNF, fallback to manual distribution
#     '''
#     try:
#         return SOLVER.to_dnf(expr)
#     except Exception:
#         return SOLVER._simplify(expr)
    
def convert_operators(expr: str) -> str:
    """
    Convert boolean expression operators:
      &  ->  &&
      |  ->  ||
      ~  ->  !
    Handles cases where && and || may already exist (won't double-expand).
    """
    # Replace | with || (but not if already ||)
    expr = re.sub(r'(?<!\|)\|(?!\|)', '||', expr)

    # Replace & with && (but not if already &&)
    expr = re.sub(r'(?<!&)&(?!&)', '&&', expr)

    # Replace ~ with !
    expr = re.sub(r'~', '!', expr)

    return expr

def simplify_to_dnf(expr_str):
    '''
    Convert conjunction -> simplified DNF -> decode string
    '''
    logical_expr = LogicalExpression(expr_str)
    solver_expr = logical_expr.to_solver_expr()
    log.debug("Converted before simplification:")
    log.debug(solver_expr)
    simplified = SOLVER._simplify(solver_expr)

    dnf_expr = str(to_dnf(str(simplified), simplify=True, force=True))
    log.debug("Simplified DNF:")
    log.debug(dnf_expr)

    converted_expr = convert_operators(dnf_expr)
    # pretty = SOLVER.pretty_print(dnf_expr)
    decoded = PM.decode_expression(str(converted_expr))
    log.debug("Decoded expression:")
    log.debug(decoded)
    log.debug("\n")

    return decoded



# =====================================================
# Join all contracts per postcondition
# =====================================================

def join_contracts_by_conjunction(A, target):
    '''
    Main function to compute final contracts
    '''

    log.debug(f'======== Start deriving final contracts =============')
    grouped = defaultdict(list)

    # grouped contracts by postcondition
    for loc in A.locations.values():
        for c in loc.contracts:
            grouped[str(c.post)].append(c)
    
    final_contracts = []

    for post_str, contracts in grouped.items():
        log.debug(f"Perform conjunction of following preconditions for {"\033[31m"}{post_str}{"\033[36m"}")

        # extract all preconditions
        pres = [c.pre for c in contracts]
        for p in pres:
            log.debug("     %s\n", p)
        log.debug("\n")

        # build conjunction
        conj_expr = build_conjunction(pres)

        # simplify + DNF
        simplified = simplify_to_dnf(conj_expr)

        final_contracts.append(
            f"{{{simplified}}} {target} {{{post_str}}}"
        )
    
    return final_contracts