from ramodel.automaton import *
from xmlparser.xmltags import *
import constraintsolver.solver as S
import xml.etree.ElementTree as ET


class ParsedXML:
    """This is a class containing methods for extracting a register automaton
    from a given XML file"""

    ###############################################
    #   constants = {id : [id_object, value]}
    #   registers = {id : id_object}
    #   method_object = Method(name, paramids)
    #   paramids = {"id" : id_obj}
    ################################################

    def __new__(self, xml_file) -> Automaton:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # obtain a dictionary of method objects
        self.methods = self.__get_methods(self, root)

        # obtain a dictionary of constants
        # constants = {id : [id_object, value]}
        self.constants = self.__get_constants(self, root)

        # obtain a dictionary of registers
        # registers = {id : id_object}
        self.registers = self.__get_registers(self, root)

        # obtain a list of outputs
        self.outputs = self.__get_outputs(self, root)

        # obtain the start location of the automaton
        self.startlocation = self.__get_start_location(self, root)

        # obtain the locations for the automaton
        self.locations = self.__get_locations(self, root)

        # extract a list of transitions from xml file
        extracted_trans = self.__get_transitions(self, root)
        # print(extractedTrans)

        # prune the list of transition by removing output locations
        self.transitions = self.__condense_automaton(self, extracted_trans)

        return Automaton(self.methods,
                         self.constants,
                         self.registers,
                         self.outputs,
                         self.transitions,
                         self.startlocation)

    def __get_methods(self, root) -> dict:
        """Method for extracting list of methods from the XML file"""
        # dict of methods
        # methods = {methodname : dict of params {param: value}}
        methods = dict()

        for inputs in root.iter(INPUTS):
            for symbol in inputs.iter(SYMBOL):
                methodname = symbol.attrib[NAME]
                # paramids = {"id" : id_obj}
                paramids = dict()
                for param in symbol.iter(PARAM):
                    paramids[param.attrib[NAME]] = S.get_int_object(param.attrib[NAME])
                    # print('id name: '+ param.attrib[NAME])

                methods[methodname] = paramids
        return methods

    def __get_constants(self, root) -> dict:
        """Method for extracting list of constants defined in the RA"""
        # dictionary of constants = {id : [id_object, value]}
        constants = dict()

        for consts in root.iter(CONSTANTS):
            for singleconst in consts.iter(CONSTANT):
                constants[singleconst.attrib[NAME]] = [S.get_int_object(singleconst.attrib[NAME]), int(singleconst.text)]
        # print(constants)
        return constants

    def __get_registers(self, root) -> dict:
        """Method for extracting global registers used in the RA"""
        # dictionary of registers = {id : id_object}
        registers = dict()

        for globals in root.iter(GLOBALS):
            for variable in globals.iter(VARIABLE):
                # storing instance of each register object into the dictionary
                registers[variable.attrib[NAME]] = S.get_int_object(variable.attrib[NAME])
        return registers

    def __get_outputs(self, root) -> dict:
        """Method for extracting all possible outputs for transitions in RA"""
        # list of outputs produce by the automaton
        products = dict()

        for outputs in root.iter(OUTPUTS):
            for symbol in outputs.iter(SYMBOL):
                # paramids = {"id" : id_obj}
                paramids = dict()
                for param in symbol.iter(PARAM):
                    paramids[param.attrib[NAME]] = S.get_int_object(param.attrib[NAME])

                products[symbol.attrib[NAME]] = paramids

        return products

    def __get_start_location(self, root) -> [Location, None]:
        """Method for extracting the starting location of the automaton"""
        for locations in root.iter(LOCATIONS):
            for location in root.iter(LOCATION):
                if INITIAL in location.attrib.keys() and location.attrib[INITIAL] == TRUE:
                    return Location(location.attrib[NAME])
        return ValueError()

    def __get_locations(self, root) -> dict:
        """Method for extracting all the locations in the RA"""
        locations = dict()
        for states in root.iter(LOCATIONS):
            for state in states.iter(LOCATION):
                if INITIAL in state.attrib.keys() and state.attrib[INITIAL] == TRUE:
                    locations[state.attrib[NAME]] = self.startlocation
                else:
                    locations[state.attrib[NAME]] = Location(state.attrib[NAME])
        # result = '\n'.join(f'{key}:{value}' for key, value in locations.items())
        # print(result)
        return locations

    def __get_transitions(self, root) -> list:
        """Method for extracting list of all the transitions in the RA"""
        progress = []
        for transitions in root.iter(TRANSITIONS):
            for transition in transitions.iter(TRANSITION):
                fromlocation = self.locations[transition.attrib[FROM]]
                tolocation = self.locations[transition.attrib[TO]]

                # obtain method name/output name causing this transition
                symbol = transition.attrib[SYMBOL]
                output = None
                if symbol in self.methods.keys():
                    method = Method(name_=symbol,
                                    paramids_=self.methods[symbol])
                elif symbol in self.outputs.keys():
                    method = output = symbol
                    for assigns in transition.iter(ASSIGNMENTS):
                        for assign in assigns.iter(ASSIGN):
                            output = assign.text if assign.attrib[TO] in self.outputs[symbol] else symbol

                # obtain guard condition for this transition
                condition = transition.find(GUARD).text if transition.find(GUARD) is not None else 'True'

                # obtain a dict of assignments performed while this transition
                assignments = dict()
                for assigns in transition.iter(ASSIGNMENTS):
                    for assign in assigns.iter(ASSIGN):
                        # assignments.append(assign.attrib[TO] + '==' + assign.text)
                        assignments[assign.attrib[TO]] = assign.text

                trans_object = Transition(fromlocation_=fromlocation,
                                          tolocation_=tolocation,
                                          method_=method,
                                          condition_=condition,
                                          assignments_=assignments,
                                          output_=output)

                # add the transition into the list of transitions
                progress.append(trans_object)
                # add the transition into the list of transitions originating at fromlocation
                fromlocation.transitions.append(trans_object)

        return progress

    def __condense_automaton(self, transitions) -> list:
        """ Method for reformatting the RA by condensing the list of transitions """
        transitions = self.__remove_output_locations(self, transitions)
        return self.__condense_constraints(self, transitions)

    def __remove_output_locations(self, transitions):
        """ Removes output locations from the RA """
        progress = []
        deletedlocations = set()
        for transition in transitions:
            # print('before pruning: ', transition)
            current_transition = transition
            current_dest = transition.toLocation
            next_transition = current_dest.transitions[0] if len(current_dest.transitions) == 1 else None
            if next_transition is not None \
                    and next_transition.method in self.outputs.keys():
                # insert the output location into the list to be deleted
                deletedlocations.add(current_dest)
                current_transition.output = next_transition.output
                current_transition.toLocation = next_transition.toLocation
            # print('after pruning: ', current_transition)

            progress.append(current_transition)

        # delete transitions originating from output locations
        [progress.remove(transition) for location in deletedlocations \
         for transition in progress if transition.fromLocation == location]

        return progress

    def __condense_constraints(self, transitions) -> list:
        """ Condense automaton by accumulating constraints
        for an observer that provides same output True or False """
        progress = list()

        for transition in transitions:
            # print('For transition: ', transition)
            for transition_ in transitions:
                # if two transitions are different
                # and their from and to locations are same
                # and both caused by the same method
                # and produce same output
                if transition != transition_ \
                        and transition.fromLocation == transition_.fromLocation \
                        and transition.toLocation == transition_.toLocation \
                        and transition.method.name == transition_.method.name \
                        and transition.output == transition_.output:
                    # print('Duplicate transition: ', transition_)
                    transition.guard = '(' + transition.guard + ') || (' + transition_.guard + ')'
                    # print('New guard: ' + transition.guard)
                    transitions.remove(transition_)

        return transitions
