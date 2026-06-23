
from common_imports import log, defaultdict

from ramodel import Automaton
from generator.postcondition_generator import generate_postconditions
from generator.contract_generator import generate_contract_per_location
from generator.simplify_new import join_contracts_by_conjunction

def log_contracts_per_location(A: Automaton):
    log.debug("Contracts derived per location:\n")
    for loc in A.locations.values():
        log.debug(f"{"\033[31m"}{loc.name}{"\033[36m"}:")
        # log.debug("%s:", loc.name)
        if not loc.contracts:
            log.debug("     No contract generated")
            continue

        for c in loc.contracts:
            log.debug("     %s", c)
        log.debug("")

        # for c in loc.contracts:
        #     print(c)

def print_final_contracts(contracts):
    for c in contracts:
        log.debug(c)

def generate(A: Automaton, target_method):
    '''
    MAIN CONTRACT SYNTHESIS DRIVER
    '''

    target = A.inputs[target_method]
    log.debug("\n")
    log.debug(f'======== Starting contract generation for method {"\033[31m"}{target}{"\033[36m"} =============')
    postconditions = generate_postconditions(A)
    for Q in postconditions:
        contracts_per_location = generate_contract_per_location(A, target, Q)

    log_contracts_per_location(A)
    final_contracts = join_contracts_by_conjunction(A, target)
    print_final_contracts(final_contracts)

    
 