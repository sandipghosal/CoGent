from common_imports import dataclass
from ramodel import Method

from .condition import Precondition, Postcondition


######################################
# Classes for holding a Contract
######################################

@dataclass(repr=False)
class Contract:
    pre: Precondition
    method: Method
    post: Postcondition

    def subsumes(self, other) -> bool:
        '''
        Check of contract C1 subsumes another contract C2
        '''
        # To be implemented
        pass

    def __str__(self):
        return f'{{{self.pre}}} {self.method} {{{self.post}}}'
    
    def __repr__(self):
        self.__str__()
