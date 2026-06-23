# test.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from build_expression import build_expr, build_logical_expr


def test_expressions():
    test_cases = [
        # Arithmetic + relational
        "(b1 == b0 + 1)",
        "p1 != b0",
        "r2 != p1 && r1 != p1",
        
        # Logical combinations
        "a == b && c == d",
        "a == b || c != d",
        "!(a == b)",
        "!(a == b && c == d)",

        # Mixed arithmetic and logical
        "b1 == b0 + 1 && p2 == b1",
        "b1 == b0 + 1 || p2 != b1",

        # Nested
        "(a == b) && (c == d)",
        "(a == b) || (c != d && e == f)",

        # Edge cases
        "a==b",
        "a+b==c",
        "x <= y + 1 && z >= t",
    ]

    print("\n========== Testing build_expr() ==========\n")

    for expr in test_cases:
        try:
            print(f"INPUT:  {expr}")

            result = build_expr(expr)

            print(f"OUTPUT: {result}")
            print("-" * 50)

        except Exception as e:
            print(f"ERROR for '{expr}': {e}")
            print("-" * 50)


def test_logical_expressions():
    test_cases = [
        "a && b",
        "a || b",
        "!(a && b)",
        "(a && b) => c",
        "(a || b) && !c",
    ]

    print("\n========== Testing build_logical_expr() ==========\n")

    for expr in test_cases:
        try:
            print(f"INPUT:  {expr}")

            result = build_logical_expr(expr)

            print(f"OUTPUT: {result}")
            print("-" * 50)

        except Exception as e:
            print(f"ERROR for '{expr}': {e}")
            print("-" * 50)


if __name__ == "__main__":
    test_expressions()
    test_logical_expressions()