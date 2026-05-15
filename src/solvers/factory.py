# import all the solvers here
from solvers.z3solver import Z3Solver
# from XSolver import xsolver

from customlogger import getlogger
log = getlogger(__name__)

SOLVER = None  # private singleton

def get_solver(name=None):
    global SOLVER

    if SOLVER is not None:
        return SOLVER

    if name is None or 'z3':
        SOLVER = Z3Solver()
        log.debug('Solver selected is: '+ 'z3')

    # elif name == 'x':
    #     SOLVER = XSolver
    else:
        log.critical('No known solver is selected')
        raise ValueError(f"Unknown Solver: {name}")
    
    return SOLVER