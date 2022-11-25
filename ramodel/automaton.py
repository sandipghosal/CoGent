class Automaton:
    def __init__(self, methods, constants, registers, transitions, startlocation) -> None:
        self.methods = methods
        # self.outputs = outputs
        self.constants = constants
        self.registers = registers
        self.transitions = transitions
        self.startLocation = startlocation


class Location:
    # Instantiate location with name and list of registers
    def __init__(self, name, transitions=None) -> None:
        self.name = name
        # list of transitions originating at this location
        self.transitions = transitions


class Register:
    def __init__(self, name, value) -> None:
        self.id = name
        self.value = value


class Method:
    # Instantiate a method with its name and list of input parameters
    def __init__(self, name, paramids) -> None:
        self.name = name
        self.paramIDs = paramids


class Parameter:
    def __init__(self, name, value) -> None:
        self.id = name
        self.value = value


class Transition:
    def __init__(self, fromlocation, tolocation, method, condition, assignments, output):
        self.fromLocation = fromlocation
        self.toLocation = tolocation
        self.method = method
        self.guard = condition
        self.assignments = assignments
        self.output = output

    def __repr__(self) -> str:
        return f'{self.fromLocation}:{self.guard}:{self.assignments}:{self.output}:{self.toLocation}'


class Guard:
    def __init__(self, ) -> None:
        pass
