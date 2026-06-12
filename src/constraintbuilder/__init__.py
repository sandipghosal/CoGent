# Old imports
from constraintbuilder.build_expression import build_expr, build_str, build_logical_expr
from constraintbuilder.constraint import *
from constraintbuilder.build_expression import Expression

# New imports
from .build_expression import Expression, LogicalExpression

__all__=[
    "Expression",
    "LogicalExpression"
]