import constraintbuilder.build_expression as BE
import constraintsolver.solver as S


def test_build_expr():
    constraint = '(a==b)||(b==c)'
    desired_expr = 'Or(a == b, b == c)'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr

    constraint = '(a==b)||(b!=c)'
    desired_expr = 'Or(a == b, Not(b == c))'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr
