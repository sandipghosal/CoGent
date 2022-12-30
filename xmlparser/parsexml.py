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

        # extract a list of transitions from xml file
        extractedTrans = self.getTransitions(self, root)
        # print(extractedTrans)

        # prune the list of transition by removing output locations
        self.transitions = self.condenseAutomaton(self, extractedTrans)

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
                paramids = []
                for param in symbol.iter(PARAM):
                    paramids.append(param.attrib[NAME])

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
                    method = output = symbol
                    for assigns in transition.iter(ASSIGNMENTS):
                        for assign in assigns.iter(ASSIGN):
                            output = assign.text if assign.attrib[TO] in self.outputs[symbol] else symbol

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

    def condenseAutomaton(self, transitions) -> list:
        progress = []
        deletelocations = set()
        for transition in transitions:
            # print('before pruning: ', transition)
            currentTransition = transition
            currentDest = transition.toLocation
            nextTransition = currentDest.transitions[0] if len(currentDest.transitions) == 1 else None
            if nextTransition is not None \
                    and nextTransition.method in self.outputs.keys():
                # insert the output location into the list to be deleted
                deletelocations.add(currentDest)
                currentTransition.output = nextTransition.output
                currentTransition.toLocation = nextTransition.toLocation
            # print('after pruning: ', currentTransition)

            progress.append(currentTransition)

        # delete transitions originating from output locations
        [progress.remove(transition) for location in deletelocations \
         for transition in progress if transition.fromLocation == location]

        return progress

