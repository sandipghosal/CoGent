import copy
import itertools
import logging
from pprint import pp

import constraintbuilder
import constraintsolver.solver as S
import import_xml
import ramodel.automaton as ra


class Monomial:
    def __init__(self, observers, condition=None, substitute=None):
        self.observers = observers
        self.condition = condition
        # list of tuples
        self.substitutes = substitute if substitute is not None else list()

    def __eq__(self, other):
        if id(self) == id(other): return True
        if len(self.observers) != len(other.observers): return False
        for i in range(len(self.observers)):
            if self.observers[i] == other.observers[i] \
                    and self.observers[i].output == other.observers[i].output:
                continue
            else:
                return False
        return True

    def __len__(self):
        return len(self.observers)

    def __repr__(self):
        string = str()
        for i in range(len(self.observers)):
            if i == 0:
                string = str(self.observers[i])
            else:
                string = string + ' and ' + str(self.observers[i])
        return string

    def subset(self, other):
        """
        Check if self is subset of other
        :param other: Object of Monomial
        :return: Boolean value True/False
        """
        # if length of other is less than self then self is not a subset
        if (len(other.observers) - len(self.observers)) < 0:
            return False

        for i in range(len(self.observers)):
            flag = False
            for j in range(len(other.observers)):
                if self.observers[i].method == other.observers[j].method \
                        and self.observers[i].output == other.observers[j].output:
                    flag = True
                    break
            if not flag:
                return False

        return True
        # for observer in self.observers:
        #     if observer in other.observers and observer.output == other.observers[
        #         other.observers.index(observer)].output:
        #         # i = other.observers.index(observer)
        #         # if observer.output == other.observers[i].output:
        #         continue
        #     else:
        #         return False


class Config:
    # Path to XML file
    PATH = None
    # Target Method object
    TARGET = None

    # Start Location
    START_LOCATION = None

    # Mapping of method name to Method object
    METHODS = dict()

    # Mapping of output name to Output object
    OUTPUTS = dict()

    # Mapping of constant name to value
    CONSTANTS = dict()

    # List of registers
    REGISTERS = list()

    # Mapping of location name to Location object
    LOCATIONS = dict()

    # Mapping of observer name to Observer object
    OBSERVERS = dict()

    # List of all possible monomials (a list of lists) sorted according to size
    # MONOMIALS = list()

    # List of all Symbols as a tuple (symbol truthvalue)
    # symbol is an object of the method
    SYMBOLS = dict()

    # List of methods that characterizes each location of an automata, e.g., isfull() or isempty()
    STATE_SYMBOLS = list()

    # Mapping of Observer to Boolean literals
    LITERALS = dict()

    def __init__(self, file):
        self.PATH = file

    def add_tranistions(self):
        """ Augment the automaton with dummy transitions """
        # loop through the list of observers in STATE_SYMBOLS
        # loop through the list of locations
        # get the list of transitions for a location wrt to an observer method
        # if there exists two transitions corresponding to each possible outcome TRUE/FALSE then do nothing
        # if there exists outcome TRUE add a transition with FALSE and vice versa
        for method in self.STATE_SYMBOLS:
            for location in self.LOCATIONS.values():
                transitions = location.get_transitions(destination=location, method=method)
                if not transitions:
                    continue
                # length should be two for two possible outputs
                if len(transitions) == 1:
                    trans = copy.copy(transitions[0])
                    # Copy create new object for the locations, hence need to reinitialize from old location
                    trans.fromLocation = transitions[0].fromLocation
                    trans.toLocation = transitions[0].toLocation
                    trans.method.guard = S._neg(transitions[0].method.guard)
                    if transitions[0].output == self.OUTPUTS['TRUE']:
                        trans.output = self.OUTPUTS['FALSE']
                        location.transitions.append(trans)
                    if transitions[0].output == self.OUTPUTS['FALSE']:
                        trans.output = self.OUTPUTS['TRUE']
                        location.transitions.append(trans)

    def populate_state_symbols(self):
        """ populate the list of methods that enable to characterize a location in the automaton """
        methods = list()
        for observer in self.OBSERVERS.values():
            methods.append(observer.method)

        for location in self.LOCATIONS.values():
            transitions = location.get_transitions(destination=location)
            for transition in transitions:
                guard = S.z3reftoStr(transition.method.guard)
                if transition.method in methods and guard not in ('True', 'False'):
                    methods.remove(transition.method)

        self.STATE_SYMBOLS = methods

    def populate_observers(self):
        observers = dict(self.METHODS)
        for location in self.LOCATIONS.values():
            for transition in location.transitions:
                if not transition:
                    break
                if transition.fromLocation != transition.toLocation \
                        and transition.method.name in observers.keys():
                    observers.pop(transition.method.name)
        for key in observers.keys():
            self.OBSERVERS[key] = ra.Observer(observers[key])


    def symbols(self):
        """ get all observer methods and associate truth values with them"""
        observers = [x.method for x in self.OBSERVERS.values()]

        # assuming observer methods have only one input parameter 'b0'
        # form the list of parameters
        params = set(['b0'])
        for x in self.TARGET.inputs:
            params.add(x)

        params = list(params)
        product_ = list()

        # if the target method has input parameters then compute all possible equalities,
        # e.g., (p1 == b0), (p1 == p1), etc.
        if len(self.TARGET.inputs):
            # obtain all possible combinations of parameters
            paramcomb = list(itertools.combinations(params, 2))
            for comb in paramcomb:
                method = ra.Method('__equality__' + str(comb), list(comb))
                product_.append((method, comb))

        for m in observers:
            if m.inputs:
                # cross product of parameterized observer and list of parameters
                product_ = product_ + list(itertools.product([m], params))
            else:
                # adding non-parameterized observer into the list with blank parameter
                product_ = product_ + [(m, '')]

        symbols = list()
        # Prepare symbols with the methods with different
        for t in product_:
            if t[0].name.find('__equality__') == -1 and t[1]:
                t[0].inputs = [t[1]]
            symbols.append(copy.copy(t[0]))

        self.SYMBOLS = [(x, y) for x in symbols for y in ['TRUE', 'FALSE']]

        logging.debug('\n\nList of symbols:')
        logging.debug(self.SYMBOLS)


    def literals(self):
        """ Obtain the list of literals from symbols """

        for t in self.SYMBOLS:
            literal = 'a' + str(len(self.LITERALS))
            observer = ra.Observer(method=t[0], literal=literal)
            if observer not in self.LITERALS.keys():
                self.LITERALS[observer] = literal

        logging.debug('\n\nList of literals:')
        logging.debug(self.LITERALS)


    def get_target(self, target):
        self.TARGET = self.METHODS[target]
        # if the target has an output paramter we need to draw that from transition
        # as the XML file do not give output parameter of a method such as pop()
        for location in self.LOCATIONS.values():
            for transition in location.transitions:
                if transition.method == self.TARGET:
                    self.TARGET.outputs = transition.output.outparams

    def print_contracts(self, message):
        logging.debug('\n\n' + message)
        for location in self.LOCATIONS.values():
            for contract in location.contracts:
                logging.debug('Location: ' + str(location) + ': ' + str(contract))
        logging.debug('\n')

    def config(self, target):
        import_xml.import_ra(self)
        self.get_target(target)
        self.populate_observers()
        self.populate_state_symbols()
        # self.add_tranistions()
        self.symbols()
        self.literals()
