class Automaton:
    """This is a class containing the data structure for holding a register automaton (RA)"""

    def __init__(self, methods_, constants_, registers_, outputs_, transitions_, startlocation_) -> None:
        self.methods = methods_
        self.constants = constants_
        self.registers = registers_
        self.outputs = outputs_
        self.transitions = transitions_
        self.startLocation = startlocation_

    def get_location(self) -> list:
        """ Method returns a list of all the locations in RA """
        locations = set()
        for transition in self.transitions:
            locations.add(transition.fromLocation)
            locations.add(transition.toLocation)
        return list(locations)

    def get_observers(self) -> list:
        """ Method returns possible list of observer methods """
        methods = list()
        for key in list(self.methods.keys()):
            methods.append(key)
        for transition in self.transitions:
            if transition.fromLocation != transition.toLocation \
                    and transition.method.name in methods:
                methods.remove(transition.method.name)
        return methods

    def get_transitions(self, source_, destination_=None, method_=None, output_=None) -> list:
        """ Returns list of transitions between a source and destination (optional)
        location for a given method (optional) and its output (optional) """
        transitions = list()
        for transition in self.transitions:
            # check if transition starting at given location
            if transition.fromLocation == source_:
                # if destination is not given
                # or destination same as input param
                if destination_ is None \
                        or destination_ == transition.toLocation:
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
        # list of transitions originating at this location
        self.transitions = list()

    def __repr__(self) -> str:
        return f'{self.name}'


class Register:
    def __init__(self, name_, value_) -> None:
        self.id = name_
        self.value = value_


class Method:
    # Instantiate a method with its name and list of input parameters
    def __init__(self, name_, paramids_=None, outputs_=None) -> None:
        self.name = name_
        self.paramIDs = paramids_
        self.outputs = outputs_

    def __repr__(self) -> str:
        return f'{self.name}:{self.paramIDs}'


class Parameter:
    def __init__(self, name_, value_=None) -> None:
        self.id = name_
        self.value = value_


class Transition:
    def __init__(self, fromlocation_, tolocation_, method_=None, condition_=None, assignments_=None, output_=None):
        self.fromLocation = fromlocation_
        self.toLocation = tolocation_
        self.method = method_
        self.guard = condition_
        self.assignments = assignments_
        self.output = output_

    def __repr__(self) -> str:
        new_line = '\n'
        return f'{new_line}{self.fromLocation}:{self.method}:{self.guard}:{self.assignments}:{self.output}:{self.toLocation}'

# class Guard:
#     def __init__(self, ) -> None:
#         pass
