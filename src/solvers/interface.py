from abc import ABC, abstractmethod

# ABC:: Abstract Base Class
# informing Python Solver is not a concrete class
# here is an interface that other class must implement

class Solver(ABC):
    ''' Abstract interface for SAT/SMT solvers '''
    
    @abstractmethod
    def int(self, id: str):
        """ Convert a string id to object of type Int """
        pass

    @abstractmethod
    def bool(self, id: str):
        """ Convert a string id to object of type Boolean """
        pass

    @abstractmethod
    def bool_val(self, arg):
        pass

    @abstractmethod
    def int_val(self, arg):
        pass

    @abstractmethod
    def function(self, id, *args):
        pass

    @abstractmethod
    def _or(self, a, b):
        pass

    @abstractmethod
    def _and(self, a, b):
        pass


    @abstractmethod
    def _neg(self, arg):
        """ Returns negation of the parameter """
        pass

    @abstractmethod
    def _ne(self, a, b):
        """ Returns not equal expression of two parameters """
        pass

    @abstractmethod
    def _eq(self, a, b):
        pass

    @abstractmethod
    def _lt(self, a, b):
        pass

    @abstractmethod
    def _gt(self, a, b):
        pass

    @abstractmethod
    def _leq(self, a, b):
        pass

    @abstractmethod
    def _geq(self, a, b):
        pass

    @abstractmethod
    def implies(self, ant, cons):
        '''
        ant: antecedent
        cons: consequent
        '''
        pass
    

    @abstractmethod
    def _add(self, a, b):
        pass

    @abstractmethod
    def _sub(self, a, b):
        pass

    @abstractmethod
    def _exists(self, vars, arg):
        pass

    @abstractmethod
    def for_all(self, vars, arg):
        pass

    @abstractmethod
    def _sat(self):
        pass

    @abstractmethod
    def _unsat(self):
        pass


    @abstractmethod
    def is_false(self, x):
        pass

    @abstractmethod
    def get_ast_id(self, x, y):
        pass

    @abstractmethod
    def _wp(self, argv, args):
        '''
        Derives the weakest precondition for a given 
        goal as input parameter
        '''
        pass


    @abstractmethod
    def substitute(self, argv, args):
        # call method to calculate weakest precondition
        pass

    
    @abstractmethod
    def _simplify(self, argv):
        pass


    @abstractmethod
    def solve(self, *args):
        # solve is do_check()
        pass

    @abstractmethod
    def is_implies(self, ante, cons):
        pass

    @abstractmethod
    def canonicalize(self, expr):
        pass
    
    @abstractmethod
    def check_equivalence(self, a, b, mode) -> bool:
        pass

    @abstractmethod
    def check_sat(self, vars, a, b):
        pass

    @abstractmethod
    def eliminate(self, argv, args):
        pass
    

    @abstractmethod
    def _str(self, argv):
        pass

    @abstractmethod
    def to_cnf(self, fml):
        pass

    @abstractmethod
    def to_dnf(self, fml):
        pass

    @abstractmethod
    def pretty_print(self, expr, val):
        pass