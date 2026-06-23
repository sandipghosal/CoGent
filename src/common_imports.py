

# -----------------------------------
# Python Specific Library
# -----------------------------------

import re
import copy
from enum import Enum, auto
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from itertools import product, permutations
from typing import List, Any, Dict, Optional, Tuple, Union


# -----------------------------------
# Project Specific Libraries
# -----------------------------------

from pathlib import Path
import xml.etree.ElementTree as ET

from customlogger import getlogger
log = getlogger(__name__)

from solvers import get_solver
SOLVER = get_solver()


# -----------------------------------
# Module Specific Classes
# -----------------------------------

# from ramodel.automaton_new import(
#     DataType, Variable, Param, OutputKind,
#     Output, Method, Location, Automaton, 
# )

# from constraintbuilder.build_expression import(
#     Expression, LogicalExpression
# )

# from conditionbuilder.predicate_manager import (
#     Predicate, ObserverPredicate,
#     EqualityPredicate, BooleanPredicate
# )

# from conditionbuilder.condition_new import(
#     Precondition, Postcondition, Conjunct
# )

# from conditionbuilder.contract import Contract

# import solvers.mus as MUS