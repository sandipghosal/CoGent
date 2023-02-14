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
    logging.debug('\n\nStarting Contract Generation')
    for location in config.LOCATIONS.values():
        for key, output in itertools.product(config.OBSERVERS, ['TRUE', 'FALSE']):
            observer = config.OBSERVERS[key]
            observer.output = config.OUTPUTS[output]
            # Obtain wp as an object of Observer class
            wp = get_wp(config, location, observer)
            if not wp: continue
            # Obtain a list of Contract objects
            contracts = get_contracts(config, location, wp)
            location.contracts = contracts
    config.print_contract('================ LIST OF ALL CONTRACTS ====================')
    refine(config)
    # pre = get_pre(automaton, target)
    # contracts = get_contracts(automaton, target, pre, wp)
    # contracts = refine(contracts)
    # contracts = synthesize(automaton, contracts)

