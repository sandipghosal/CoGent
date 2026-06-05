
from ramodel.automaton_new import Automaton
from generator.postcondition_generator import generate_postconditions
from generator.contract_generator import generate_contract_per_location
from customlogger import getlogger
log = getlogger(__name__)


def generate(A: Automaton, target_method):
    '''
    MAIN CONTRACT SYNTHESIS DRIVER
    '''

    target = A.inputs[target_method]
    log.debug(f'======== Starting contract generation for method {"\033[31m"}{target}{"\033[36m"} =============')
    postconditions = generate_postconditions(A)
    for Q in postconditions:
        contracts_per_location = generate_contract_per_location(A, target, Q)
 