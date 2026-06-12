# Old import
from ramodel.config import Config
from ramodel.automaton import *


# New import
from .automaton_new import(
    DataType,
    Variable,
    Param,
    OutputKind,
    Output,
    Method,
    Location,
    Automaton
)

__all__ = [
    "DataType",
    "Variable",
    "Param",
    "OutputKind",
    "Output",
    "Method",
    "Location",
    "Automaton",
]