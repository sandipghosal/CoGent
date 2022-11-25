from xmlparser.xmltags import *
from ramodel.automaton import *

import xml.etree.ElementTree as ET


class ParsedXML:

    def __init__(self, xml_file) -> Automaton:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # obtain a dictionary of method objects
        methods = self.getMethods(root)

        # obtain a dictionary of constants
        constants = self.getConstants(root)

        # obtain a dictionary of registers
        registers = self.getRegisters(root)

        # obtain the start location of the automaton
        startlocation = self.getStartLocation(root)

        # obtain the locations for the automaton
        locations = self.getLocations(root)

        # obtain a tree of transitions
        transitions = self.getTransitions()

        return Automaton(methods, constants, registers, transitions, startlocation)

    def getMethods(self, root) -> dict:
        # list of method objects
        methods = dict()

        for inputs in root.iter(INPUTS):
            for symbol in inputs.iter(SYMBOL):
                method = symbol.attrib[NAME]
                # print('method name: ' + method)
                paramids = dict()
                for param in symbol.iter(PARAM):
                    paramids[param.attrib[NAME]] = Parameter(param.attrib[NAME], None)
                    # print('id name: '+ param.attrib[NAME])

                methods[method] = Method(method, paramids)

        return methods

    def getConstants(self, root) -> dict:
        # dictionary of constants {key : value}
        constants = dict()

        for consts in root.iter(CONSTANTS):
            for singleconst in consts.iter(CONSTANT):
                constants[singleconst.attrib[NAME]] = int(singleconst.text)

        # print(constants)
        return constants

    def getRegisters(self, root) -> dict:
        # dictionary of registers {key  : value}
        registers = dict()

        for globals in root.iter(GLOBALS):
            for variable in globals.iter(VARIABLE):
                registers[variable.attrib[NAME]] = Register(variable.attrib[NAME], None)
        # print(registers)
        return registers

    def getStartLocation(self, root) -> [str, None]:
        for locations in root.iter(LOCATIONS):
            for location in root.iter(LOCATION):
                if INITIAL in location.attrib.keys() and location.attrib[INITIAL] == TRUE:
                    return location.attrib[NAME]
        return None

    def getLocations(self, root) -> dict:
        locations = dict()
        for states in root.iter(LOCATIONS):
            for state in states.iter(LOCATION):
                locations[Location(state.attrib[NAME])] = Location(state.attrib[NAME])
        return locations

    def getTransitions(self, root):
        progress = []
        for transitions in root.iter(TRANSITIONS):
            for transition in root.iter(TRANSITION):
                print()

    # create a tree of tranistions for an automaton
    # def transitions(self):
    #     transition = self.getTransitions()
    #     return transition