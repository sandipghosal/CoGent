from common_imports import Dict
from ramodel import Variable, DataType


class FreeVariablePool:
    """
    Stores all free variables used in contracts
    (e.g., b0, b1, ...)
    """

    def __init__(self):
        self.vars: Dict[str, Variable] = {}
        self.counter = 0

    def new(self, typ: DataType) -> Variable:
        name = f"b{self.counter}"
        self.counter += 1

        v = Variable(name=name, typ=typ)
        v.constant = False   # explicitly free

        self.vars[name] = v
        return v

    def get_all(self):
        return list(self.vars.values())

    def __contains__(self, name):
        return name in self.vars

    def __getitem__(self, name):
        return self.vars[name]


FV = FreeVariablePool()