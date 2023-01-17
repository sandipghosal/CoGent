class Automaton:
    """ Class containing the data structure for holding a register automaton (RA) """

    def __init__(self, methods_, constants_, registers_, locations_, transitions_) -> None:
        self.methods = methods_
        self.constants = constants_
        self.registers = registers_
        self.locations = locations_
        self.transitions = transitions_

    def get_locations(self) -> list:
        """ Method returns a list of Location objects for all the locations in RA """
        locations = set()
        for transition in self.transitions:
            locations.add(transition.fromlocation)
            locations.add(transition.tolocation)
        return list(locations)

    def get_destinations(self, sourceloc_, method_=None) -> list:
        """ Returns a list of target locations from
        a given source location and a method (optional) """
        locations = set()
        for transition in self.transitions:
            if transition.fromlocation == sourceloc_:
                if method_ is None \
                        or transition.method.name == method_:
                    locations.add(transition.tolocation)
        return list(locations)

    def get_observers(self) -> list:
        """ Method returns possible list of observer methods """
        methods = list()
        for key in list(self.methods.keys()):
            methods.append(key)
        for transition in self.transitions:
            if transition.fromlocation != transition.tolocation \
                    and transition.method.name in methods:
                methods.remove(transition.method.name)
        return methods

    def get_transitions(self, source_, destination_=None, method_=None, output_=None) -> list:
        """ Returns list of transitions between a source and destination (optional)
        location(s) for a given method (optional) and its output (optional) """
        transitions = list()
        for transition in self.transitions:
            # check if transition starting at given location
            if transition.fromlocation == source_:
                # if destination is not given
                # or destination same as input param
                if destination_ is None \
                        or destination_ == transition.tolocation:
                    # check if the transition caused by the method
                    # is same as given in the input parameter
                    if method_ is None \
                            or method_ == transition.method.name:
                        # if the output param is not specified
                        # or equal to the output of the transition
                        if output_ is None \
                                or transition.output == output_:
                            transitions.append(transition)
        return transitions


class Location:
    # Instantiate location with name and list of registers
    def __init__(self, name_) -> None:
        self.name = name_

    def __eq__(self, other):
        if not isinstance(other, Location):
            return None
        return self.name == other.name and id(self) == id(other)

    def __hash__(self):
        return id(self)

    def __repr__(self) -> str:
        return f'{self.name}'


class Method:
    # Instantiate a method with its name and list of input parameters
    def __init__(self, name_, params_=None, output_=None) -> None:
        self.name = name_
        self.inparams = params_
        self.outparams = output_

    def __repr__(self) -> str:
        return f'{self.name}:{self.inparams}:{self.outparams}'


class Transition:
    def __init__(self, fromlocation_, tolocation_, method_=None,
                 condition_=None, assignments_=None, output_= None):
        self.fromlocation = fromlocation_
        self.tolocation = tolocation_
        self.method = method_
        self.guard = condition_
        self.assignments = assignments_
        self.output = output_

    def __repr__(self) -> str:
        # new_line = '\n'
        return f'{self.fromlocation}:{self.method}:{self.guard}:{self.assignments}:{self.output}:{self.tolocation}'
