import itertools
import logging
from pprint import pp

import constraintsolver.solver as S
from contract.contract import *
from ramodel import Method


################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
### Precondition:: list of Observer output,
###################################################


def getcontract(automaton, target, pre, wp):
    logging.debug('\n\nStarting Contract Generation')
    contract = list()
    targetobj = Method(name_=target, params_=automaton.methods[target])
    # gather registers that would be needed for checking validity
    reg = list()
    for id_ in automaton.registers.keys():
        reg.append(automaton.registers[id_])
    logging.debug('List of defined registers: ' + str(reg))

    # gather defined constants that would be needed to
    # substitute constant values before checking validity
    const = list()
    for id_ in automaton.constants.keys():
        const.append((automaton.constants[id_][0], automaton.constants[id_][1]))
    logging.debug('List of defined constants: ' + str(const))

    # gather the list of parameters
    params = set()
    for x in automaton.methods[target]:
        params.add(S._int(x))

    for location in automaton.get_locations():
        logging.debug('\nGenerate contract at ' + str(location))
        for precond in pre[location]:
            for post in wp[location]:
                logging.debug('Precondition: ' + str(precond))
                logging.debug('Postcondition: ' + str(post))

                for x in post.params:
                    params.add(x)

                contract.append(Contract(target=targetobj,
                                         location=location,
                                         params=list(params),
                                         registers=reg,
                                         constants=const,
                                         precondition=precond,
                                         postcondition=post))
    return contract


def getpre(automaton, target):
    # initialize the mapping for containing all
    # the mappings of location to preconditions
    pre = dict()

    # obtain the list of observer methods
    observers = automaton.get_observers()

    # considering observer methods have only one input parameter 'b0'
    # form the list of parameters
    params = ['b0']
    for x in automaton.methods[target]:
        params.append(x)

    product_ = list(itertools.product(observers, params))

    # generate the monomials
    temp = [list(zip(product_, x)) for x in itertools.product(['TRUE', 'FALSE'], repeat=len(product_))]
    # massage the final list of monomials: list of lists
    # each inner list is a tuple (methodname, output, param)
    monomials = [[(inner[0][0], inner[1], inner[0][1]) for inner in outer] for outer in temp]

    logging.debug('All possible monomials:')
    logging.debug(pp(monomials))

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

                observer = Observer(name=method,
                                    condition=transition[0].guard,
                                    output=output,
                                    subargs=subargs)
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


def getwp(automaton, target):
    # initialize the dictionary for containing all
    # the mappings of location to postconditions
    wp = dict()

    # for each of the location in automaton
    for location in automaton.get_locations():

        logging.debug('Evaluating weakest precondition at location: ' + str(location))

        # initialize the list for containing the postconditions
        postconds = list()

        # for each of the observer in the automaton
        for obsname in automaton.get_observers():

            # prepare the substitution for param ids
            subargs = list()
            params = automaton.methods[obsname]
            for i in range(len(params)):
                subargs.append((S._int(params[i]), S._int('b' + str(i))))

            # for each kind of possible output (later extend beyond true/false)
            for output in ['TRUE', 'FALSE']:
                logging.debug('Evaluate WP for ' + obsname + ' == ' + output)
                # initialize the list of (transition, postobserver) tuples
                args = list()

                # for each transition originating from this location
                for transition in automaton.get_transitions(source_=location, method_=target):
                    # obtain the destination location
                    dest = transition.tolocation

                    # obtain the transitions for observer at destination
                    obstrans = automaton.get_transitions(source_=dest,
                                                         destination_=dest,
                                                         method_=obsname,
                                                         output_=output)

                    # if obstrans is empty continue with next transition
                    if not obstrans:
                        continue

                    logging.debug('Consider transitions at post-state:')
                    logging.debug(obstrans)

                    # obtain the condition for observer at destination
                    obscond = obstrans[0].guard
                    # create an observer object
                    observer = Observer(name=obsname,
                                        condition=obscond,
                                        output=output, subargs=subargs)

                    logging.debug('Observer method at destination:')
                    logging.debug(observer)

                    # add (transition, observer) tuple into the list
                    args.append((transition, observer))

                if not args:
                    continue
                # obtain the weakest precondition for obsname and output
                wpobject = WeakestPrecondition(args)

                postconds.append(Postcondition(observername=obsname,
                                               params=[s[1] for s in subargs],
                                               output=output,
                                               weakestpre=wpobject))

        # insert a map from location to postcondition list
        wp[location] = postconds

    logging.debug('\n\n============ LIST OF WEAKEST PRECONDITION ===============')
    for location in automaton.get_locations():
        logging.debug('AT LOCATION: ' + str(location))
        for wpcond in wp[location]:
            logging.debug(str(wpcond.condition) + ' to satisfy ' + str(wpcond))
    # return the mapping from location to list of postconditions
    return wp


def generate(automaton, target):
    wp = getwp(automaton, target)
    pre = getpre(automaton, target)
    contract = getcontract(automaton, target, pre, wp)
    return contract
