import itertools

from constraint_builder.build_expression import build_expr
from constraintsolver.solver import *


def generate(automaton, modifier):
    """ Function perform the steps for generating contract for a given method """

    observers = automaton.get_observers()
    # get_preconditions(automaton, observers, automaton.startLocation)
    for observer in observers:
        for output in ['TRUE', 'FALSE']:
            # list of visited locations
            visited = list()
            # queue of locations pending to visit
            queue = list()
            queue.append(automaton.startLocation)
            visited.append(automaton.startLocation)
            # while queue is not empty
            while queue:
                # pop a location from the queue
                location = queue.pop(0)

                # obtain the transitions originating from the location due to the given modifier
                transitions = automaton.get_transitions(source_=location, method_=modifier)

                # derive weakest precondition at this location w.r.t. the observer and its output
                weakest_pre = get_weakest_precondition(automaton, transitions, observer, output)
                print('At location', location, 'for post-condition', observer, ' == ', output, '::')
                print('wp: ', weakest_pre)
                # list of all possible preconditions at the pre-location
                preconditions = get_preconditions(automaton, observers, location)

                # check for the satisfiability if each precondition
                # does satisfy the weakest precondition
                for condition in preconditions:
                    condition = do_simplify(condition)
                    result = get_implies(condition, weakest_pre)
                    print(result, do_check(result), end='\n\n')

                # insert the destination locations from this location into the queue
                for transition in transitions:
                    if transition.toLocation not in visited:
                        queue.append(transition.toLocation)
                        visited.append(transition.toLocation)


def get_preconditions(automaton, observers, location):
    # initialize the list of possible pre-conditions
    preconditions = list()

    # populate a list of transitions considered while obtaining precondition
    precond_transitions = list()

    # obtain list of transitions at location
    transitions = automaton.get_transitions(source_=location, destination_=location)

    # obtains monomials of all observers: a list of lists
    monomials = [list(zip(observers, x)) for x in itertools.product(['TRUE', 'FALSE'], repeat=len(observers))]
    # print(monomials)
    for item in monomials:
        # each element item is a list of tuples of observers
        # with respective Boolean output TRUE/FALSE
        result = None
        for i in range(len(item)):

            # iterate through all transitions due to observers at given location
            for j in range(len(transitions)):
                # if the transition method is same as the item[i][0]
                # and produce same output as item[i][1]
                if transitions[j].method.name == item[i][0] \
                        and transitions[j].output == item[i][1]:

                    # insert the transition into the list of transitions considered
                    precond_transitions.append(transitions[j])

                    # for first transition set the result
                    if i == 0:
                        result = get_constraint(automaton, transitions[j], transitions[j].guard)
                    else:
                        # for the subsequent transitions do the conjunction with previous result
                        result = get_and(
                            result,
                            get_constraint(automaton, transitions[j], transitions[j].guard)
                        )
        if result is not None: preconditions.append(result)

    return preconditions


def get_weakest_precondition(automaton, transitions, observer, observer_output):
    """ Returns a BoolRef object at a given location for
    a method and an output of observer method """
    # obtain disjunction of all the constraints for the list of transitions
    disjunctions = constraints_disjunction(automaton, transitions)

    # derive the conjunction of implications: if guard of the modifier is true
    # then the guard of the observer should hold
    implications = implication_to_postcondition(automaton, transitions, observer, observer_output)

    # obtain the weakest pre-condition by doing conjunction of disjunction and implications
    # and further simplification
    return do_simplify(get_and(disjunctions, implications))


def constraints_disjunction(automaton, transitions):
    """ Returns BoolRef object: disjunctions of constraints
    for the given transitions """
    result = None
    for index in range(len(transitions)):
        if index == 0:
            # for first index get the z3 constraint
            result = get_constraint(automaton, transitions[index], transitions[index].guard)
        else:
            # for next transition do OR with previous results
            result = get_or(result, get_constraint(automaton, transitions[index], transitions[index].guard))
    return result


def implication_to_postcondition(automaton, transitions, observer, output):
    """ Returns BoolRef object: implication of
    modifier constraint to observer constraint """
    # set implication to None: variable contains weakest pre-condition
    # derived from the assignment and post-condition
    implications = None

    # iterate the loop for each transition originating at a location
    for index in range(len(transitions)):
        # derive the wp for modifier assignment where
        # observer constraint is the post-condition
        obs_transition = automaton.get_transitions(source_=transitions[index].toLocation,
                                                   destination_=transitions[index].toLocation,
                                                   method_=observer,
                                                   output_=output)

        # there should be only one transition for the
        # observer method giving a specific output True or False
        if len(obs_transition) > 1: ValueError()

        # from the mapping assignment create a list of tuples
        # of the format [(key, value)] where key and value are z3 objects
        modifier_assigns = list()
        for key in transitions[index].assignments.keys():
            modifier_assigns.append((get_constraint(automaton, transitions[index], key),
                                     get_constraint(automaton, transitions[index],
                                                    transitions[index].assignments[key])))
        # print('Modifier transition: ', transitions[index])
        # print(modifier_assigns)
        # print('Observer transition: ', obs_transition)

        # obtain weakest pre-condition derived from the assignment and post-condition
        weakest_p = weakest_precondition(get_constraint(automaton, obs_transition[0], obs_transition[0].guard),
                                         modifier_assigns)
        # print('weakest pre: ', weakest_p)

        # obtain the conjunction of implications
        if index == 0:
            implications = get_implies(get_constraint(automaton, transitions[index], transitions[index].guard),
                                       weakest_p)
        else:
            implications = get_and(implications,
                                   get_implies(get_constraint(automaton, transitions[index], transitions[index].guard),
                                               weakest_p)
                                   )
        return implications


def get_constraint(automaton, transition, expression):
    return build_expr(automaton, transition, expression)
