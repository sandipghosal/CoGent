import logging
from pprint import pp
import xml.etree.ElementTree as ET
from import_xml.extract import extract
from errors import *


def condense(automaton):
    """ Join constraints of multiple transitions for
    an observer method giving same output in a location """
    newlist = list()

    for outer in automaton.transitions:
        for inner in automaton.transitions:
            # if two transitions are different
            # and their from and to locations are same
            # and both caused by the same method
            # and produce same output
            if outer != inner \
                    and outer.fromlocation == inner.fromlocation \
                    and outer.tolocation == inner.tolocation \
                    and outer.method.name == inner.method.name \
                    and outer.output == inner.output:
                outer.guard = (outer.guard)._or(inner.guard)
                automaton.transitions.remove(inner)
    logging.debug('\n\nNew list of transitions after condensing:')
    logging.debug(pp(automaton.transitions))
    return automaton


def pruning(automaton):
    """ Removes output locations from the RA """
    # new list of tranistions
    newlist = list()

    # set of locations to be removed from the automaton
    locations = set()

    transitions = automaton.transitions

    for transition in transitions:
        current_trans = transition
        current_dest = transition.tolocation

        next_trans = automaton.get_transitions(current_dest)
        if len(next_trans) == 1:
            if next_trans[0].method not in automaton.methods.keys():
                locations.add(current_dest)
                current_trans.output = next_trans[0].output
                current_trans.tolocation = next_trans[0].tolocation
            else:
                raise ValueNotFound('Pruning failed for destination of transition: ' + str(transition))

        newlist.append(current_trans)

    # delete transitions originating from output locations
    [newlist.remove(transition) for location in locations \
     for transition in newlist if transition.fromlocation == location]

    # set the pruned list of transitions to automaton
    automaton.transitions = newlist

    logging.debug('\n\nNew list of transitions after pruning:')
    logging.debug(pp(automaton.transitions))

    return automaton


def import_ra(file):
    """ Import a register automaton from an input XML file """
    try:
        tree = ET.parse(file)
    except:
        InvalidInputFile('Invalid input file: ' + file)

    ra = condense(pruning(extract(tree)))
    # pruning(ra)
    # condense(ra)
    return ra
