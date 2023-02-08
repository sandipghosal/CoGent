

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






def generate(automaton, target):
    wp = get_wp(automaton, target)
    pre = get_pre(automaton, target)
    contracts = get_contracts(automaton, target, pre, wp)
    # contracts = refine(contracts)
    contracts = synthesize(automaton, contracts)
    return contracts
