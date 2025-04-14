import constraintbuilder.build_expression as BE
import smtsolvers.solver as S


def test_build_expr():
    constraint = 'isfull && isempty => false'
    desired_expr = 'Implies(And(isfull, isempty), False)'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr

    constraint = 'a==b && b==c'
    desired_expr = 'And(a == b, b == c)'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr

    constraint = 'a==b||b!=c'
    desired_expr = 'Or(a == b, Not(b == c))'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr

    constraint = 'r2!=p1 && r3!=p1 && r1!=p1'
    desired_expr = 'And(Not(r2 == p1), Not(r3 == p1)), Not(r1 == p1))'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr

    constraint = '(a0 and a1) => false'
    desired_expr = 'Implies(And(a0,a1), False)'
    expr = BE.build_expr(constraint)
    recvd_expr = S.z3reftoStr(expr)
    assert recvd_expr == desired_expr
