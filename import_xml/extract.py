from import_xml.xmltags import *
from ramodel.automaton import *
from constraint_builder.build_expression import build_expr
import constraintsolver.solver as S


def get_transitions(root, methods, constants, registers, locations):
    # populate the list of Transition objects
    progress = list()

    for transitions in root.iter(TRANSITIONS):
        for transition in transitions.iter(TRANSITION):
            fromlocation = locations[transition.attrib[FROM]]
            tolocation = locations[transition.attrib[TO]]

            # obtain method name/output name causing this transition
            symbol = transition.attrib[SYMBOL]

            # initialize a list of output parameters
            outputs = list()

            # store a Method object
            method = None
            if symbol in methods.keys():
                # create a Method object of input symbol
                method = Method(name_=symbol, params_=methods[symbol])
            else:
                for assigns in transition.iter(ASSIGNMENTS):
                    for assign in assigns.iter(ASSIGN):
                        if assign.attrib[TO]: outputs.append(assign.text)
                    else:
                        outputs.append(symbol)
                # create a Method object of output symbol
                method = Method(name_=symbol, output_=outputs)

            # obtain guard condition for this transition
            expression = transition.find(GUARD).text if transition.find(GUARD) is not None else 'True'
            condition = build_expr(expression, method, registers, constants)

            # obtain a list of assignments performed while this transition
            # list of tuples of the format [(key, value)] where key and value are z3 objects
            assignments = list()
            for assigns in transition.iter(ASSIGNMENTS):
                for assign in assigns.iter(ASSIGN):
                    # assignments.append(assign.attrib[TO] + '==' + assign.text)
                    assignments.append((build_expr(assign.attrib[TO], method, registers, constants),
                                        build_expr(assign.text, method, registers, constants)))

            trans_object = Transition(fromlocation_=fromlocation,
                                      tolocation_=tolocation,
                                      method_=method,
                                      condition_=condition,
                                      assignments_=assignments)

            # add the transition into the list of transitions
            progress.append(trans_object)

    return progress


def get_locations(root):
    # dictionary of locations = {name: Location object}
    locations = dict()

    for states in root.iter(LOCATIONS):
        for state in states.iter(LOCATION):
            locations[state.attrib[NAME]] = Location(state.attrib[NAME])
    return locations


def get_registers(root):
    # dictionary of registers = {id : Int Object}
    registers = dict()
    for _globals in root.iter(GLOBALS):
        for variable in _globals.iter(VARIABLE):
            # storing instance of each register object into the dictionary
            registers[variable.attrib[NAME]] = S.get_int_object(variable.attrib[NAME])
    return registers


def get_constants(root):
    # dictionary of constants = {id : [Int Object, value]}
    constants = dict()
    for consts in root.iter(CONSTANTS):
        for _id in consts.iter(CONSTANT):
            constants[_id.attrib[NAME]] = [S.get_int_object(_id.attrib[NAME]), int(_id.text)]
    # print(constants)
    return constants


def get_methods(root):
    # methods = {name : list of params [param1, param2,..]}
    methods = dict()
    for inputs in root.iter(INPUTS):
        for symbol in inputs.iter(SYMBOL):
            name = symbol.attrib[NAME]
            params = list()
            for param in symbol.iter(PARAM):
                params.append(param.attrib[NAME])
            methods[name] = params
    return methods


def extract(tree):
    root = tree.getroot()
    methods = get_methods(root)
    constants = get_constants(root)
    registers = get_registers(root)
    locations = get_locations(root)
    transitions = get_transitions(root, methods, constants, registers, locations)
