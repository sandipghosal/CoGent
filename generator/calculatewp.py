import copy
import logging

import smtsolvers.solver as S

automaton = None
location = None
observer = None


def get_disjunction(args, index, result=None):
    """
    Obtain disjunction of all the constraints for the list of transitions
    :param args: list of tuples (transition, postcondition)
    :param index: current index of args list
    :param result: result of disjunction; default is None
    :return: BoolRef object result, disjunction of all constraints for the transitions
    """
    if index == 0:
        return get_disjunction(args, index + 1, (args[index][0]).method.guard)
    elif index == len(args):
        return result
    else:
        return S._or(result, get_disjunction(args, index + 1, (args[index][0]).method.guard))


def get_implication(args):
    """
    Obtain disjunction of all the constraints for the list of transitions
    :param args: list of tuples (transition, postcondition)
    :return: BoolRef object result, disjunction of all constraints for the transitions
    """

    result = None
    # for each of the tuple in the list
    for index in range(len(args)):
        wp = S.weakest_pre(args[index][1].method.guard, args[index][0].assignments)
        if index == 0:
            result = S._implies(args[index][0].method.guard, wp)
        else:
            result = S._and(result, S._implies(args[index][0].method.guard, wp))

    return result


def get_observer_at_poststate(substitutes):
    global automaton, location, observer
    # initialize the list of (transition, postobserver) tuples
    args = list()

    # for each transition originating from this location
    for transition in location.get_transitions(method=automaton.TARGET):
        # obtain the destination location
        dest = transition.toLocation
        # obtain the transitions for observer at destination
        obstrans = dest.get_transitions(destination=dest,
                                        method=observer.method,
                                        output=observer.output)
        # if obstrans is empty continue with next transition
        if not obstrans:
            continue

        # obtain the observer method for this transition at destination
        method = copy.deepcopy(obstrans[0].method)
        # change the input parameter of the method
        method.inputs = [S.z3reftoStr(x[1]) for x in substitutes]
        # obtain the condition for observer at destination

        method.guard = S.do_substitute(obstrans[0].method.guard, substitutes)
        # create an observer object
        newobserver = copy.deepcopy(automaton.OBSERVERS[method.name])
        newobserver.method = method
        newobserver.output = observer.output

        logging.debug('\n')
        # add (transition, observer) tuple into the list
        args.append((transition, newobserver))

    return args


def get_observer_for_wp():
    global location, observer

    _args = list()
    # prepare the substitution for param ids
    params = observer.method.inputs
    for i in range(len(params)):
        _args.append((S._int(params[i]), S._int('b' + str(i))))
    # gather a list of (transition, postobserver) tuples
    # respective to eah transition originating at current location
    args = get_observer_at_poststate(_args)

    # if there is no such transition corresponding to the observer in any of the post states
    # create a new observer with guard condition False
    if not args:
        # first check if the observer is one of the STATE_SYMBOLS, like isfull()/isempty() and
        # check if the observer at all has any transition (that outputs True/False)
        # at this location, then create a dummy observer for isfull()/isempty() even though
        # it does not appear in the RA
        if observer.method in automaton.STATE_SYMBOLS \
                and (location.get_transitions(method=observer.method, output=automaton.OUTPUTS['TRUE'])
                     or location.get_transitions(method=observer.method, output=automaton.OUTPUTS['FALSE'])):
            newobserver = copy.deepcopy(observer)
            newobserver.method.guard = S._boolval(False)
            newobserver.literal = automaton.LITERALS[observer]
            return newobserver

        else:
            return None

    # obtain the weakest precondition for observer and output
    wp = S.do_simplify(S._and(get_disjunction(args, 0), get_implication(args)))

    newobserver = copy.deepcopy(args[0][1])
    newobserver.method.guard = wp
    newobserver.literal = automaton.LITERALS[args[0][1]]
    return newobserver


def get_wp(config, location_, observer_):
    global automaton, location, observer
    automaton = config
    location = location_
    observer = observer_
    # initialize the dictionary for containing all
    # the mappings of location to postconditions
    wp = get_observer_for_wp()
    return wp
