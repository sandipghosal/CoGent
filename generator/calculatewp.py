import logging
from generator.conditions import *
import constraintsolver.solver as S

automaton = None
target = None


def get_disjunction(args, index, result=None):
    """
    Obtain disjunction of all the constraints for the list of transitions
    :param args: list of tuples (transition, postcondition)
    :param index: current index of args list
    :param result: result of disjunction; default is None
    :return: BoolRef object result, disjunction of all constraints for the transitions
    """
    if index == 0:
        return get_disjunction(args, index + 1, (args[index][0]).guard)
    elif index == len(args):
        return result
    else:
        return S._or(result, get_disjunction(args, index + 1, (args[index][0]).guard))

    # for index in range(len(args)):
    #     if index == 0:
    #         # for first index get the z3 constraint
    #         result = (args[index][0]).guard
    #     else:
    #         # for next transition do OR with previous results
    #         result = S._or(result, (args[index][0]).guard)
    #
    # return result


def get_implication(args):
    """
    Obtain disjunction of all the constraints for the list of transitions
    :param args: list of tuples (transition, postcondition)
    :return: BoolRef object result, disjunction of all constraints for the transitions
    """

    result = None
    # for each of the tuple in the list
    for index in range(len(args)):
        wp = S.weakest_pre(args[index][1].guard, args[index][0].assignments)
        if index == 0:
            result = S._implies(args[index][0].guard, wp)
        else:
            result = S._and(result, S._implies(args[index][0].guard, wp))

    return result


def get_observer_at_poststate(location, observer, output, substitutes):
    logging.debug('Obtain WP for ' + observer + ' == ' + output)
    # initialize the list of (transition, postobserver) tuples
    args = list()

    # for each transition originating from this location
    for transition in automaton.get_transitions(source_=location, method_=target):
        # obtain the destination location
        dest = transition.tolocation

        # obtain the transitions for observer at destination
        obstrans = automaton.get_transitions(source_=dest,
                                             destination_=dest,
                                             method_=observer,
                                             output_=output)
        # if obstrans is empty continue with next transition
        if not obstrans:
            continue

        logging.debug('Consider transitions at post-state:')
        logging.debug(obstrans)

        # obtain the condition for observer at destination
        guard = obstrans[0].guard
        # create an observer object
        observer = Condition(name=observer,
                             condition=guard,
                             output=output, args=substitutes)

        logging.debug('Observer method at destination:')
        logging.debug(observer)

        # add (transition, observer) tuple into the list
        args.append((transition, observer))

    return args


def get_wp_at_location(location):
    logging.debug('Evaluating weakest precondition at location: ' + str(location))

    # initialize the list for containing the postconditions
    postconds = list()

    # for each of the observer in the automaton
    for observer in automaton.get_observers():
        # prepare the substitution for param ids
        _args = list()
        params = automaton.methods[observer]
        for i in range(len(params)):
            _args.append((S._int(params[i]), S._int('b' + str(i))))
        for output in ['TRUE', 'FALSE']:
            # gather a list of (transition, postobserver) tuples
            # respective to eah transition originating at current location
            args = get_observer_at_poststate(location, observer, output, _args)
            if not args:
                continue
            # obtain the weakest precondition for observer and output
            wp = S.do_simplify(S._and(get_disjunction(args, 0),
                                      get_implication(args)))

            postconds.append(Postcondition(name=observer,
                                           precondition=wp,
                                           output=output,
                                           args= _args))

    return postconds


def get_wp(automaton_, target_):
    # initialize global automaton and target
    global automaton, target
    automaton = automaton_
    target = target_

    # initialize the dictionary for containing all
    # the mappings of location to postconditions
    wp = dict()
    for location in automaton.get_locations():
        conditions = get_wp_at_location(location)
        wp[location] = conditions
    return wp
