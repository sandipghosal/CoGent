import logging
from pprint import pp

import constraintsolver.solver as S
from contract.contract import *


################# Data Structure ##################
### Map of States = {l0, l1, ... , ln}
### Each state maps to an object of Postcondition
### Postcondition:: observername, params, output, weakestpre
###################################################


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
        print('AT LOCATION:', location)
        pp(postconds)
    # return the mapping from location to list of postconditions
    return wp


def generate(automaton, target):
    wp = getwp(automaton, target)
