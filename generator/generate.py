

from generator.calculatewp import get_wp
from generator.contract import get_contract
from generator.obtainpre import get_pre



################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
### Precondition:: list of Observer output,
###################################################






def generate(automaton, target):
    wp = get_wp(automaton, target)
    pre = get_pre(automaton, target)
    contract = get_contract(automaton, target, pre, wp)
    return contract
