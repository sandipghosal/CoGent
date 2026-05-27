import itertools
import logging

from generator.calculatewp import get_wp
from generator.contract import get_contracts
from generator.simplify import synthesize
import generator.invariant as INV


from customlogger import getlogger
log = getlogger(__name__)


################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
### Precondition:: list of Observer output,
###################################################


