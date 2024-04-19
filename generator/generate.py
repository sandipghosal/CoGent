import itertools
import logging

from generator.calculatewp import get_wp
from generator.contract import get_contracts
from generator.simplify import synthesize
import generator.invariant as INV


################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
### Precondition:: list of Observer output,
###################################################


def generate(config):
    logging.debug('\n\n=========== Starting Contract Generation =================')
    INV.generate_invariants(config)
    for location in config.LOCATIONS.values():
        invariants = config.get_invariants(location)
        for key, output in itertools.product(config.OBSERVERS, ['TRUE', 'FALSE']):
            observer = config.OBSERVERS[key]
            observer.output = config.OUTPUTS[output]
            logging.debug('\n')
            logging.debug('Generating contract at location: ' + str(location))
            logging.debug('Observer method at post-state: ' + str(observer))
            # Obtain wp as an object of Observer class
            wp = get_wp(config, location, observer)
            if not wp:
                logging.debug('Derived weakest precondition: None')
                continue
            logging.debug('Derived weakest precondition:' + str(wp.method.guard))
            # Obtain a list of Contract objects
            contracts = get_contracts(config, location, wp, invariants)
            [location.contracts.append(contract) for contract in contracts]
            logging.debug('\n')
            logging.debug('Location specific contracts after adding invariants:')
            [logging.debug(c) for c in contracts]
    config.print_contracts('================ CONTRACTS PER LOCATION ====================')
    # refine(config)
    synthesize(config)
