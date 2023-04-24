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
        if self.name in ('True', 'False'):
            return str(self.name)
        elif self.name.find('__equality__') != -1:
            string = str()
            for i in range(len(self.inputs)):
                if string == '':
                    string = str(self.inputs[i])
                else:
                    string = string + ' == ' + self.inputs[i]
            return string
            # return str(self.guard)
        else:
            return self.name + '(' + ', '.join(self.inputs) + ')'

    def __hash__(self):
        return hash(str(self.name))

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
        if self.method.name in ('True', 'False'):
            return str(self.method)
        elif self.method.name.find('__equality__') != -1:
            if not self.output:
                return str(self.method)
            else:
                return '(' + str(self.method) + ')' if self.output.name == 'TRUE' else 'Not(' + str(self.method) + ')'
        elif not self.output:
            return str(self.method)
        elif str(self.output.name) == 'TRUE':
            return str(self.method) + ' == ' + str(True)
        elif str(self.output.name) == 'FALSE':
            return str(self.method) + ' == ' + str(False)
            # return str(self.method) + ' == ' + str(self.output)
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
        # return self.name == other.name
        return id(self) == id(other) or self.name == other.name

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

    def get_contracts(self, pre=None, post=None):
        """
        Returns the list of contracts with matching given observer as postcondition
        :param observer: an Observer object with output
        :return: a list of Contract objects
        """
        if not self.contracts:
            return []
        contracts = list()
        for contract in self.contracts:
            if pre is None \
                    or contract.pre == pre:
                if post is None \
                        or contract.post == post:
                    contracts.append(contract)
        return contracts
