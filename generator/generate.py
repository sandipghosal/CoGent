import sys

from constraint_builder.build_expression import build_expr


def generate(automaton, method):
    """ Function perform the steps for generating contract for a given method """
    # foreach observer method
    #   set an output first
    #   generate contract considering the output as post-condition

    # observers = automaton.get_observers()
    # for observer in observers:
    #     for output in ['TRUE','FALSE']:
    #         for location in automaton.get_location():
    #             pass


    for transition in automaton.transitions:
        get_constraint(automaton, transition)



def get_constraint(automaton, transition):
    build_expr(automaton, transition)
