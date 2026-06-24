
import re

# eq_pattern = r"""
#     [A-Za-z_][A-Za-z0-9_]*(?:\([^()]*\))?   # LHS
#     \s*
#     (==|!=)
#     \s*
#     [A-Za-z0-9_+\-*/]+(?:\s*[+\-*/]\s*[A-Za-z0-9_]+)*   # RHS
# """



eq_pattern = r"""
    [A-Za-z_][A-Za-z0-9_]*(?:\([^()]*\))?   # LHS
    \s*
    (?:==|!=)
    \s*
    (
        \(
            [A-Za-z0-9_]+
            (?:\s*[+\-*/]\s*[A-Za-z0-9_]+)+
        \)
        |
        [A-Za-z0-9_]+
    )
"""



text = "p0 == b1 || I_size() == b0 && I_contains(p1) || b0==(b1+1) && b1==(b0-1)"

matches = [m.group() for m in re.finditer(eq_pattern, text, re.VERBOSE)]

for m in sorted(matches, key=len, reverse=True):
    print(m)
