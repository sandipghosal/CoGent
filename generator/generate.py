import itertools
import logging

from generator.calculatewp import get_wp
from generator.contract import get_contracts
from generator.obtainpre import get_pre
from generator.refine import refine
from generator.synthesize import synthesize


################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
### Precondition:: list of Observer output,
###################################################







def generate(config):
    logging.debug('\n\n=========== Starting Contract Generation =================')
    for location in config.LOCATIONS.values():
        for key, output in itertools.product(config.OBSERVERS, ['TRUE', 'FALSE']):
            observer = config.OBSERVERS[key]
            observer.output = config.OUTPUTS[output]
            # Obtain wp as an object of Observer class
            wp = get_wp(config, location, observer)
            if not wp: continue
            # Obtain a list of Contract objects
            contracts = get_contracts(config, location, wp)
            [location.contracts.append(contract) for contract in contracts]
    config.print_contracts('================ LIST OF VALID CONTRACTS ====================')

    # for location in config.LOCATIONS.values():
    #     location.contracts[:] = [item for item in location.contracts if item.result == True]
    # config.print_contract('================ LIST OF ALL VALID CONTRACTS ====================')
    
    refine(config)
    # synthesize(config)

