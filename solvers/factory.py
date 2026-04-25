# import all the solvers here
from z3solver import Z3Solver
# from XSolver import xsolver

SOLVER = None  # private singleton

def get_solver(name: str='z3'):
    global SOLVER

    if SOLVER is not None:
        return SOLVER
    
    name = name.lower()

    if name == 'z3':
        SOLVER = Z3Solver()
    # elif name == 'x':
    #     SOLVER = XSolver
    else:
        raise ValueError(f"Unknown Solver: {name}")
    
    return SOLVER