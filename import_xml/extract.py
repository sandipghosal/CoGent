import copy
import logging
from pprint import pp

import constraintbuilder
import smtsolvers.solver as S
from import_xml.xmltags import *
from ramodel.automaton import *

ROOT = None


def condense(transitions, config):
    """ Join constraints of multiple transitions for
    an observer method giving same output in a location """
    deletedtransition = set()
    for outer in transitions:
        if outer in deletedtransition:
            continue
        for inner in transitions:
            # if two transitions are different
            # and their from and to locations are same
            # and both caused by the same method
            # and produce same output
            if outer != inner \
                    and outer.fromLocation == inner.fromLocation \
                    and outer.toLocation == inner.toLocation \
                    and outer.method == inner.method \
                    and outer.output == inner.output:
                outer.method.guard = S._or(outer.method.guard, inner.method.guard)
                deletedtransition.add(inner)

    # delete the transitions after condensing
    for transition in deletedtransition:
        for location in config.LOCATIONS.values():
            if transition in location.transitions:
                location.transitions.remove(transition)

    logging.debug('\n\nNew list of transitions after condensing:')
    logging.debug(transitions)


def pruning(transitions, config):
    """ Removes output locations from the RA """
    # new list of tranistions
    newlist = list()

    deletedlocations = set()
    for transition in transitions:
        current_trans = transition
        current_dest = transition.toLocation
        next_transition = current_dest.transitions[0] if len(current_dest.transitions) == 1 else None
        if next_transition is not None \
                and next_transition.method.name in config.OUTPUTS:
            # insert the output location into the list to be deleted
            deletedlocations.add(current_dest)
            current_trans.output = next_transition.method
            current_trans.assignments = current_trans.assignments + next_transition.assignments
            current_trans.toLocation = next_transition.toLocation



        newlist.append(current_trans)

    # delete transitions originating from output locations
    [newlist.remove(transition) for location in deletedlocations \
     for transition in newlist if transition.fromLocation == location]

    logging.debug('\n\nNew list of transitions after pruning:')
    logging.debug(newlist)

    for location in deletedlocations: del (config.LOCATIONS[location.name])

    logging.debug('\n\nNew list of locations after pruning:')
    logging.debug(config.LOCATIONS)

    return newlist


def get_transitions(config):
    # populate the list of Transition objects
    progress = list()

    for transitions in ROOT.iter(TRANSITIONS):
        for transition in transitions.iter(TRANSITION):
            # get the source and destination location of a transition
            fromloc = config.LOCATIONS[transition.attrib[FROM]]
            toloc = config.LOCATIONS[transition.attrib[TO]]

            # obtain method name/output name causing this transition
            symbol = transition.attrib[SYMBOL]

            # initialize the output and method of the tranisition as None
            output = method = None

            if symbol in config.METHODS.keys():
                # copy a Method object
                method = copy.deepcopy(config.METHODS[symbol])
            if symbol in config.OUTPUTS.keys():
                method = copy.deepcopy(config.OUTPUTS[symbol])
            # else:
            #     # create a Method object of output symbol with output parameters
            #     method.outparams = outputs[symbol]
            #     output = symbol
            #     for assigns in transition.iter(ASSIGNMENTS):
            #         for assign in assigns.iter(ASSIGN):
            #             output = assign.text if assign.attrib[TO] in outputs[symbol] else symbol

            # obtain guard condition for this transition
            expression = transition.find(GUARD).text if transition.find(GUARD) is not None else 'True'
            method.guard = constraintbuilder.build_expr(expression)

            # obtain a list of assignments performed while this transition
            # list of tuples of the format [(key, value)] where key and value are z3 objects
            assignments = list()
            for assigns in transition.iter(ASSIGNMENTS):
                for assign in assigns.iter(ASSIGN):
                    # assignments.append(assign.attrib[TO] + '==' + assign.text)
                    assignments.append((constraintbuilder.build_expr(assign.attrib[TO]),
                                        constraintbuilder.build_expr(assign.text)))

            trans_object = Transition(fromloc=fromloc,
                                      toloc=toloc,
                                      method=method,
                                      assignments=assignments,
                                      output=output)

            logging.debug('Transition created:')
            logging.debug(trans_object)
            # add the transition into the list of transitions
            progress.append(trans_object)
            # add the transition into the toloc Location object
            config.LOCATIONS[str(fromloc)].transitions.append(trans_object)

    # logging.debug('List of transitions imported from the file:')
    # logging.debug(pp(progress))
    return progress


def get_outputs():
    """Method for extracting all possible outputs for transitions in RA"""
    # list of outputs produce by the automaton
    products = dict()

    for outputs in ROOT.iter(OUTPUTS):
        for symbol in outputs.iter(SYMBOL):
            # params = ['id1', ..]
            params = list()
            for param in symbol.iter(PARAM):
                params.append(param.attrib[NAME])

            name = None
            if name in ['TRUE', 'True', 'true']:
                name = True
            elif name in ['FALSE', 'False', 'false']:
                name = False
            else:
                name = symbol.attrib[NAME]

            products[symbol.attrib[NAME]] = Output(name, params)

    logging.debug('Map of output symbols imported from the file:')
    logging.debug(products)
    return products


def get_start_location():
    for locations in ROOT.iter(LOCATIONS):
        for location in ROOT.iter(LOCATION):
            if INITIAL in location.attrib.keys() and location.attrib[INITIAL] == TRUE:
                return location.attrib[NAME]
    return None


def get_locations():
    # dictionary of locations = {name: Location object}
    locations = dict()

    for states in ROOT.iter(LOCATIONS):
        for state in states.iter(LOCATION):
            locations[state.attrib[NAME]] = Location(state.attrib[NAME])

    logging.debug('Map of locations imported from the file:')
    logging.debug(locations)

    return locations


def get_registers():
    # list of registers
    registers = list()
    for _globals in ROOT.iter(GLOBALS):
        for variable in _globals.iter(VARIABLE):
            # storing instance of each register object into the dictionary
            registers.append(variable.attrib[NAME])

    logging.debug('List of registers imported from the file:')
    logging.debug(registers)
    return registers


def get_constants():
    # dictionary of constants = {id : value}
    constants = dict()
    for consts in ROOT.iter(CONSTANTS):
        for _id in consts.iter(CONSTANT):
            constants[_id.attrib[NAME]] = int(_id.text)

    logging.debug('Map of constants imported from the file:')
    logging.debug(constants)
    return constants


def get_methods():
    # methods = {name : Method Object}
    methods = dict()
    for inputs in ROOT.iter(INPUTS):
        for symbol in inputs.iter(SYMBOL):
            name = symbol.attrib[NAME]
            params = list()
            for param in symbol.iter(PARAM):
                params.append(param.attrib[NAME])
            methods[name] = Method(name, params)

    logging.debug('Map of input symbols imported from the file:')
    logging.debug(methods)
    return methods


def extract(tree, config):
    global ROOT
    ROOT = tree.getroot()
    config.METHODS = get_methods()
    config.CONSTANTS = get_constants()
    config.REGISTERS = get_registers()
    config.LOCATIONS = get_locations()
    config.START_LOCATION = config.LOCATIONS[get_start_location()]
    config.OUTPUTS = get_outputs()

    transitions = get_transitions(config)
    condense(pruning(transitions, config), config)

    # extra work for bad XML file
    # remove blank locations
    for location in config.LOCATIONS.copy():
        if not config.LOCATIONS[location].transitions:
            config.LOCATIONS.pop(location)
