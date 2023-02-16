import copy
import itertools
import logging
from pprint import pp

import constraintbuilder
import import_xml
import ramodel.automaton as ra


class Monomial:
    def __init__(self, observers, condition=None):
        self.observers = observers
        self.condition = condition

    def __eq__(self, other):
        return self.observers == other.observers

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

        for observer in self.observers:
            if observer in other.observers and observer.output == other.observers[
                other.observers.index(observer)].output:
                # i = other.observers.index(observer)
                # if observer.output == other.observers[i].output:
                continue
            else:
                return False

        return True


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

    # Mapping of observer name to Method object
    OBSERVERS = dict()

    # List of all possible monomials (a list of lists) sorted according to size
    MONOMIALS = list()

    # Mapping of Observer to Boolean literals
    LITERALS = dict()

    def __init__(self, file):
        self.PATH = file

    def get_observers(self):
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

    def get_monomials(self):
        # considering observer methods have only one input parameter 'b0'
        # form the list of parameters
        params = ['b0']
        for x in self.TARGET.inputs:
            params.append(x)

        product_ = list()

        # obtain all possible combinations of parameters
        paramcomb = list(itertools.combinations(params, 2))
        for comb in paramcomb:
            observer = ra.Observer(ra.Method('__equality__' + str(comb)))
            # self.OBSERVERS['__equality__' + str(comb)] = observer
            product_.append((observer, comb))

        # for i in range(len(self.OBSERVERS)):
        for key in self.OBSERVERS.keys():
            observer = list()
            observer.append(self.OBSERVERS[key])
            if self.OBSERVERS[key].method.inputs:
                # cross product of parameterized observers and parameters
                product_ = product_ + list(itertools.product(observer, params))
            else:
                # adding non-parameterized observer into the list with blank parameter
                product_ = product_ + [(self.OBSERVERS[key], '')]

        # Following 8 lines will generate monomials for
        # all possible combinations of 1 to len(product_) sizes
        combinations = list()
        for i in range(1, len(product_) + 1):
            for comb in itertools.combinations(product_, i):
                combinations.append(comb)
        temp = list()
        for index in range(len(combinations)):
            comb = [x for x in combinations[index]]
            temp.append([list(zip(comb, x)) for x in itertools.product(['TRUE', 'FALSE'], repeat=len(comb))])

        # Following statement will generate possible combinations of observer methods
        # for fixed size, i.e., length of product_
        # temp = [list(zip(product_, x)) for x in itertools.product(['TRUE', 'FALSE'], repeat=len(product_))]

        # generate the monomials
        # massage the final list of monomials
        # each inner list is a tuple (methodname, output, param)
        for i in range(len(temp)):
            for item in temp[i]:
                observers = list()
                for x in item:
                    # create a copy of the Observer object
                    observer = copy.deepcopy(x[0][0])
                    # change the input parameter of the Method object
                    if observer.method.name.find('__equality__') != -1:
                        # the observer testing parameters' equality
                        observer.method.inputs = list(x[0][1])
                        if x[1] == 'TRUE':
                            observer.method.guard = constraintbuilder.build_expr(x[0][1][0] + ' == ' + x[0][1][1])
                        else:
                            observer.method.guard = constraintbuilder.build_expr(x[0][1][0] + ' != ' + x[0][1][1])
                    else:
                        # the observer is something else
                        if x[0][1] != '':
                            observer.method.inputs = [x[0][1]]

                    observer.output = self.OUTPUTS[x[1]]

                    if observer not in self.LITERALS:
                        observer.literal = 'a' + str(len(self.LITERALS))
                        self.LITERALS[observer] = observer.literal
                    else:
                        observer.literal = self.LITERALS[observer]
                    observers.append(observer)

                self.MONOMIALS.append(Monomial(observers))

        # sort the monomials as per the number of observers in a monomial
        self.MONOMIALS.sort(key=lambda x: len(x))

        # monomials of observer methods for fixed size i.e., length of product_
        # monomials = [[(inner[0][0], inner[1], inner[0][1]) for inner in outer] for outer in temp]

        logging.debug('List of monomials:')
        logging.debug(pp(self.MONOMIALS))

    def print_contracts(self, message):
        logging.debug('\n\n' + message)
        for location in self.LOCATIONS.values():
            for contract in location.contracts:
                logging.debug('Location: ' + str(location) + ': {' + str(contract.monomial) + '} ' + str(self.TARGET) +
                              ' {' + str(contract.wp) + '} :: ' + str(contract.result))
        logging.debug('\n')

    def config(self, target):
        import_xml.import_ra(self)
        self.TARGET = self.METHODS[target]
        self.get_observers()
        self.get_monomials()
