class Automaton:
    def __init__(self, methods, constants, registers, outputs, transitions, startlocation) -> None:
        self.methods = methods
        self.constants = constants
        self.registers = registers
        self.outputs = outputs
        self.transitions = transitions
        self.startLocation = startlocation


class Location:
    # Instantiate location with name and list of registers
    def __init__(self, name) -> None:
        self.name = name
        # list of transitions originating at this location
        self.transitions = list()

    def __repr__(self) -> str:
        return f'{self.name}'

class Register:
    def __init__(self, name, value) -> None:
        self.id = name
        self.value = value


class Method:
    # Instantiate a method with its name and list of input parameters
    def __init__(self, name, paramids=None, outputs=None) -> None:
        self.name = name
        self.paramIDs = paramids
        self.outputs = outputs

    def __repr__(self) -> str:
        return f'{self.name}:{self.paramIDs}:{self.outputs}'

class Parameter:
    def __init__(self, name, value=None) -> None:
        self.id = name
        self.value = value


class Transition:
    def __init__(self, fromlocation, tolocation, method=None, condition=None, assignments=None, output=None):
        self.fromLocation = fromlocation
        self.toLocation = tolocation
        self.method = method
        self.guard = condition
        self.assignments = assignments
        self.output = output

    def __repr__(self) -> str:
        new_line = '\n'
        return f'{new_line}{self.fromLocation}:{self.guard}:{self.assignments}:{self.output}:{self.toLocation}'



# class Guard:
#     def __init__(self, ) -> None:
#         pass
