from xmlparser.xmltags import *
from ramodel.automaton import *

import xml.etree.ElementTree as ET


class ParsedXML:

    def __new__(self, xml_file) -> Automaton:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # obtain a dictionary of method objects
        self.methods = self.getMethods(self, root)

        # obtain a dictionary of constants
        self.constants = self.getConstants(self, root)

        # obtain a dictionary of registers
        self.registers = self.getRegisters(self, root)

        # obtain a list of outputs
        self.outputs = self.getOutputs(self, root)

        # obtain the start location of the automaton
        self.startlocation = self.getStartLocation(self, root)

        # obtain the locations for the automaton
        self.locations = self.getLocations(self, root)

        # obtain a tree of transitions
        self.transitions = self.getTransitions(self, root)

        return Automaton(self.methods,
                         self.constants,
                         self.registers,
                         self.outputs,
                         self.transitions,
                         self.startlocation)

    def getMethods(self, root) -> dict:
        # dict of methods
        # methods = {methodname : dict of params {param: value}}
        methods = dict()

        for inputs in root.iter(INPUTS):
            for symbol in inputs.iter(SYMBOL):
                methodname = symbol.attrib[NAME]
                # print('method name: ' + method)
                paramids = dict()
                for param in symbol.iter(PARAM):
                    paramids[param.attrib[NAME]] = param.attrib[NAME]
                    # print('id name: '+ param.attrib[NAME])

                methods[methodname] = paramids
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
                # storing instance of each register object into the dictionary
                # registers[variable.attrib[NAME]] = Register(variable.attrib[NAME], None)
                registers[variable.attrib[NAME]] = int(variable.text)
        return registers

    def getOutputs(self, root) -> dict:
        # list of outputs produce by the automaton
        products = dict()

        for outputs in root.iter(OUTPUTS):
            for symbol in outputs.iter(SYMBOL):
                paramids = dict()
                for param in symbol.iter(PARAM):
                    paramids[param.attrib[NAME]] = param.attrib[NAME]

                products[symbol.attrib[NAME]] = paramids

        return products

    def getStartLocation(self, root) -> [Location, None]:
        for locations in root.iter(LOCATIONS):
            for location in root.iter(LOCATION):
                if INITIAL in location.attrib.keys() and location.attrib[INITIAL] == TRUE:
                    return Location(location.attrib[NAME])
        return None

    def getLocations(self, root) -> dict:
        locations = dict()
        for states in root.iter(LOCATIONS):
            for state in states.iter(LOCATION):
                locations[state.attrib[NAME]] = Location(state.attrib[NAME])
        # result = '\n'.join(f'{key}:{value}' for key, value in locations.items())
        # print(result)
        return locations

    def getTransitions(self, root) -> list:
        progress = []
        for transitions in root.iter(TRANSITIONS):
            for transition in transitions.iter(TRANSITION):
                fromlocation = self.locations[transition.attrib[FROM]]
                tolocation = self.locations[transition.attrib[TO]]

                # obtain method name/output name causing this transition
                symbol = transition.attrib[SYMBOL]
                output = None
                if symbol in self.methods.keys():
                    method = Method(name=symbol,
                                    paramids=self.methods[symbol])
                elif symbol in self.outputs.keys():
                    output = symbol

                # obtain guard condition for this transition
                condition = transition.find(GUARD).text if transition.find(GUARD) is not None else 'True'

                # obtain the assignments performed while this transition
                assignments = dict()
                for assigns in transition.iter(ASSIGNMENTS):

                    for assign in assigns.iter(ASSIGN):
                        assignments[assign.attrib[TO]] = assign.text

                transObject = Transition(fromlocation=fromlocation,
                                         tolocation=tolocation,
                                         method=method,
                                         condition=condition,
                                         assignments=assignments,
                                         output=output)

                # add the transition into the list of transitions
                progress.append(transObject)
                # add the transition into the list of transitions originating at fromlocation
                fromlocation.transitions.append(transObject)

        return progress

                        # lhs = assign.attrib[TO]
                        # rhs = assign.text


                        # print(lhs + ':' + rhs)

                        # both LHS and RHS of the assignment are registers
                        # if all(key in self.registers.keys()
                        #        for key in (lhs, rhs)):
                        #     # print('LHS and RHS both registers')
                        #     assignments[self.registers[lhs]] = self.registers[rhs]

                        # only LHS is a register and RHS is a constant
                        # elif all(key in [self.registers.keys(), self.constants.keys()]
                        #          for key in (lhs, rhs)):
                        #     # print('LHS is a register and RHS is a constant')
                        #     assignments[self.registers[lhs]] = self.constants[rhs]
                        #
                        # # LHS is an input/output parameter and RHS is a constant
                        # elif rhs in self.constants.keys():
                        #     # all(key in (self.methods[methodname].keys() or self.outputs[output].keys() or
                        #     #              self.constants.keys())
                        #     #      for key in (lhs, rhs)):
                        #     # print('LHS is a parameter and RHS is a constant')
                        #     assignments[Parameter(name=lhs)] = self.constants[rhs]
                        #
                        # # only LHS is a register and RHS is a parameter
                        # elif lhs in self.registers.keys():
                        #     # print('LHS is a register and RHS is a parameter')
                        #     assignments[self.registers[lhs]] =
                        # # LHS is a parameter and RHS is a register
                        # else:
                        #     print('LHS is a parameter and RHS is a register')


    # create a tree of tranistions for an automaton
    # def transitions(self):
    #     transition = self.getTransitions()
    #     return transition
