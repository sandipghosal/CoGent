import sys

from expression_builder.build_expression import build_expr


def generate(automaton, method):
    """This function perform the steps for generating contract for a given method"""
    # foreach observer method
    #   set an output first
    #   generate contract considering the output as post-condition

    # observers = automaton.getObservers()
    # for observer in observers:
    #     for output in ['TRUE','FALSE']:

    for transition in automaton.transitions:
        process(automaton, transition)


def process(automaton, transition):
    build_expr(automaton, transition)
