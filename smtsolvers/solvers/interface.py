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
    def _or(self, first, second):
        pass

    @abstractmethod
    def _and(self, first, second):
        pass


    @abstractmethod
    def _neg(self, arg):
        """ Returns negation of the parameter """
        pass

    @abstractmethod
    def _ne(self, first, second):
        """ Returns not equal expression of two parameters """
        pass

    @abstractmethod
    def _eq(self, first, second):
        pass

    @abstractmethod
    def _lt(self, first, second):
        pass

    @abstractmethod
    def _gt(self, first, second):
        pass

    @abstractmethod
    def _leq(self, first, second):
        pass

    @abstractmethod
    def _geq(self, first, second):
        pass

    @abstractmethod
    def implies(self, first, second):
        pass
    

    @abstractmethod
    def _add(self, first, second):
        pass

    @abstractmethod
    def _sub(self, first, second):
        pass

    @abstractmethod
    def _exists(self, vars, arg):
        pass

    @abstractmethod
    def for_all(self, vars, arg):
        pass

    @abstractmethod
    def sat(self):
        pass

    @abstractmethod
    def unsat(self):
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
    def check_equivalence(self, first, second) -> bool:
        pass

    @abstractmethod
    def check_sat(self, vars, first, second):
        pass

    @abstractmethod
    def eliminate(self, argv, args):
        pass
    

    @abstractmethod
    def str(self, argv):
        pass