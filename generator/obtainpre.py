import itertools
import logging
from pprint import pp

import constraintbuilder.build_expression as BE
import constraintsolver.solver as S
from generator.conditions import Condition, Precondition

automaton = None
target = None


def generate_pre(monomials):
    # initialize the mapping for containing all
    # the mappings of location to preconditions
    pre = dict()

    # iterate for each location in the automaton
    for location in automaton.get_locations():
        logging.debug('Start deriving precondition for location: ' + str(location))
        # create a list of preconditions for each row
        conditions = list()
        # iterate over the list of monomials
        for row in monomials:
            logging.debug('Consider the row ' + str(row))
            # create a list of observer objects for each tuple
            obslist = list()

            # gather conjunction of each observer guard
            result = None

            # iterate over each tuple in the row
            for index in range(len(row)):
                method = row[index][0]
                output = row[index][1]
                inputid = row[index][2]

                if type(method) is tuple:
                    expr = None
                    if output == 'TRUE':
                        expr = method[0] + ' == ' + method[1]
                        expr = BE.build_expr(expr)
                    if output == 'FALSE':
                        expr = method[0] + ' != ' + method[1]
                        expr = BE.build_expr(expr)
                    if result is not None:
                        result = S._and(result, expr)

                    observer = Condition(name='__equality__',
                                         condition=expr,
                                         output=output,
                                         args=[])
                    obslist.append(observer)
                    continue
                # obtain the transition for the method and output
                logging.debug('Fetching transition for method ' + method + '(' + inputid + ')' + ' == ' + output)
                transition = automaton.get_transitions(source_=location,
                                                       destination_=location,
                                                       method_=method,
                                                       output_=output)

                logging.debug('Transition obtained : ' + str(transition))
                # if transition is empty continue with next transition
                if not transition:
                    continue

                # prepare the substitution for param ids
                subargs = list()
                params = automaton.methods[method]
                for i in range(len(params)):
                    subargs.append((S._int(params[i]), S._int(inputid)))

                observer = Condition(name=method,
                                     condition=transition[0].guard,
                                     output=output,
                                     args=subargs)
                logging.debug('Observer object created for: ' + str(observer))

                # add the observer into the list
                obslist.append(observer)

                if index == 0 or result is None:
                    result = observer.guard
                else:
                    result = S._and(result, observer.guard)

            # insert an object of Precondition into the list
            if result is not None:
                conditions.append(Precondition(observers=obslist, condition=result))
            else:
                logging.warning('No precondition generated')

        # insert a map entry from the location to list of preconditions
        pre[location] = conditions

    logging.debug('\n\n============ LIST OF PRECONDITION ===============')
    for location in automaton.get_locations():
        logging.debug('AT LOCATION: ' + str(location))
        for precond in pre[location]:
            logging.debug(str(precond) + ' :: ' + str(precond.condition))
    return pre


def generate_monomials():
    # obtain the list of observer methods
    observers = automaton.get_observers()

    # considering observer methods have only one input parameter 'b0'
    # form the list of parameters
    params = ['b0']
    for x in automaton.methods[target]:
        params.append(x)

    product_ = list()
    for i in range(len(observers)):
        observer = list()
        observer.append(observers[i])
        if automaton.methods[observers[i]]:
            # cross product of parameterized observers and parameters
            product_ = product_ + list(itertools.product(observer, params))
        else:
            # adding non-parameterized observer into the list with blank parameter
            product_ = product_ + [(observer[0], '')]

    # obtain all possible combinations of parameters
    paramcomb = list(itertools.combinations(params, 2))
    for comb in paramcomb:
        product_.append((comb, ''))

    # generate the monomials
    temp = [list(zip(product_, x)) for x in itertools.product(['TRUE', 'FALSE'], repeat=len(product_))]
    # massage the final list of monomials: list of lists
    # each inner list is a tuple (methodname, output, param)
    monomials = [[(inner[0][0], inner[1], inner[0][1]) for inner in outer] for outer in temp]
    logging.debug('List of monomials:')
    logging.debug(pp(monomials))
    return monomials


def get_pre(automaton_, target_):
    global automaton, target
    automaton = automaton_
    target = target_

    monomials = generate_monomials()
    pre = generate_pre(monomials)
    return pre
