import logging


class Output:
    def __init__(self, name, params=None):
        self.name = name
        self.outparams = params

    def __eq__(self, other):
        return self.name == other.name and self.outparams == other.outparams

    def __repr__(self):
        return str(self.name)


class Method:
    # Instantiate a method with its name and list of input parameters
    def __init__(self, name, inparams=None, outparams=None) -> None:
        self.name = name
        self.inputs = inparams
        self.outputs = outparams
        self.guard = None

    def __repr__(self):
        if self.name.find('__equality__') != -1:
            return self.inputs[0] + ' == ' + self.inputs[1]
        else:
            return self.name + '(' + str(*self.inputs) + ')'

    def __eq__(self, other):
        return self.name == other.name


class Observer(Method):
    def __init__(self, method, literal=None, output=None):
        self.method = method
        self.literal = literal
        self.output = output

    def __eq__(self, other):
        # comparing output would produce different literals for same observer with different outputs
        return self.method == other.method and self.method.inputs == other.method.inputs


    def __hash__(self):
        return hash(str(self.method) + str(self.method.inputs))

    def __repr__(self):
        if self.method.name.find('__equality__') != -1:
            return '(' + str(self.method) + ')' if self.output.name == 'TRUE' else 'Not(' + str(self.method) + ')'
        elif self.output is not None:
            return str(self.method) + ' == ' + str(self.output)
        else:
            return str(self.method)


class Transition:
    def __init__(self, fromloc, toloc, method, assignments, output):
        self.fromLocation = fromloc
        self.toLocation = toloc
        self.method = method
        self.assignments = assignments
        self.output = output

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return f'{self.fromLocation}:{self.method}:{self.method.guard}:{self.assignments}:{self.output}:{self.toLocation}'


class Location:
    # Instantiate location with name and list of registers
    def __init__(self, name):
        self.name = name
        self.transitions = list()
        self.contracts = list()

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return self.name

    def get_transitions(self, destination=None, method=None, output=None):
        """
        Returns list of transitions between a source and destination (optional)
        location(s) for a given method (optional) and its output (optional)
        :param destination: Destination Location object
        :param method:      Method object
        :param output:      Output object
        :return:            List of Transition objects
        """
        if self.transitions is None:
            return []
        transitions = list()
        for transition in self.transitions:
            # if destination is not given
            # or destination same as input param
            if destination is None \
                    or destination == transition.toLocation:
                # check if the transition caused by the method
                # is same as given in the input parameter
                if method is None \
                        or method == transition.method:
                    # if the output param is not specified
                    # or equal to the output of the transition
                    if output is None \
                            or transition.output == output:
                        transitions.append(transition)
        return transitions

    def get_destinations(self, method=None):
        """
        Returns a list of target locations from
        this location and a method (optional)
        :param method:
        :return: List of Location objects
        """
        locations = set()
        for transition in self.transitions:
            if method is None \
                    or transition.method == method:
                locations.add(transition.toLocation)
        return list(locations)


#
# class Automaton:
#     """ Class containing the data structure for holding a register automaton (RA) """
#
#     def __init__(self, methods_, constants_, registers_, locations_, transitions_) -> None:
#         self.methods = methods_
#         self.constants = constants_
#         self.registers = registers_
#         self.locations = locations_
#         self.transitions = transitions_
#
#     def get_locations(self) -> list:
#         """ Method returns a list of Location objects for all the locations in RA """
#         locations = set()
#         for transition in self.transitions:
#             locations.add(transition.fromlocation)
#             locations.add(transition.tolocation)
#         return list(locations)
#
#     def get_destinations(self, sourceloc_, method_=None) -> list:
#         """ Returns a list of target locations from
#         a given source location and a method (optional) """
#         locations = set()
#         for transition in self.transitions:
#             if transition.fromlocation == sourceloc_:
#                 if method_ is None \
#                         or transition.method.name == method_:
#                     locations.add(transition.tolocation)
#         return list(locations)
#
#     def get_observers(self) -> list:
#         """ Method returns possible list of observer methods """
#         methods = list()
#         for key in list(self.methods.keys()):
#             methods.append(key)
#         for transition in self.transitions:
#             if transition.fromlocation != transition.tolocation \
#                     and transition.method.name in methods:
#                 methods.remove(transition.method.name)
#         return methods
#
#     def get_transitions(self, source_, destination_=None, method_=None, output_=None) -> list:
#         """ Returns list of transitions between a source and destination (optional)
#         location(s) for a given method (optional) and its output (optional) """
#         transitions = list()
#         for transition in self.transitions:
#             # check if transition starting at given location
#             if transition.fromlocation == source_:
#                 # if destination is not given
#                 # or destination same as input param
#                 if destination_ is None \
#                         or destination_ == transition.tolocation:
#                     # check if the transition caused by the method
#                     # is same as given in the input parameter
#                     if method_ is None \
#                             or method_ == transition.method.name:
#                         # if the output param is not specified
#                         # or equal to the output of the transition
#                         if output_ is None \
#                                 or transition.output == output_:
#                             transitions.append(transition)
#         return transitions
