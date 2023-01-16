import os
import getopt
import datetime

from errors import *
from import_xml import import_ra


def setuplogger(switch, logfile, loglevel=None):
    logpath = 'log'
    exist = os.path.exists(logpath)
    # if log directory does not exist create one
    if not exist:
        os.makedirs(logpath)

    if not switch:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    if switch:
        if logfile is None:
            # create a default log file using the timestamp
            logfile = 'log/' + str(datetime.datetime.now()).split(' ')[1] + '.log'
        else:
            logfile = 'log/' + logfile
        if loglevel:
            logging.basicConfig(filename=logfile, level=loglevel)
        else:
            logging.basicConfig(filename=logfile, level=logging.DEBUG)
        print('log file created:' + logfile)


def main(argv):
    try:
        if len(argv) == 0:
            raise ValueError()

        options, arguments = getopt.getopt(sys.argv[1:],
                                           "hi:t:l:g:",
                                           ["help",
                                            "input=",
                                            "target=",
                                            "log=",
                                            "log-level="])

        xmlfile = target = logfile = level = None
        logswitch = False

        for option, argument in options:
            if option in ("-h", "--help"):
                print('python main.py -i <XML file> -t <Target Method> -l <Log file> -g <ERROR|DEBUG>')
                sys.exit()

            elif option in ("-i", "--input"):
                xmlfile = argument

            elif option in ("-t", "--target"):
                target = argument

            elif option in ("-l", "--log"):
                logswitch = True
                logfile = argument

            elif option in ("-g", "--log-level"):
                levels = {"ERROR": logging.ERROR,
                          "INFO": logging.INFO,
                          "DEBUG": logging.DEBUG}
                level = levels.get(option, logging.NOTSET)

    except (ValueError, getopt.GetoptError):
        print('python main.py -h [--help]')
        sys.exit(2)

    # set up the logging environment
    setuplogger(switch=logswitch, logfile=logfile, loglevel=level)

    # import the automaton from the XML file
    automaton = None

    # check if user has provided the XML file
    try:
        if not xmlfile:
            raise InputsNotFound('XML file not found')
        elif not target:
            raise InputsNotFound('Target method not found')
        else:
            logging.debug(pp('input XML file path: ' + xmlfile))
    except (InputsNotFound, getopt.GetoptError):
        print('python main.py -h [--help]')
        sys.exit(2)

    automaton = import_ra(xmlfile)
    # generate(automaton, 'I_push')


    # print(automaton.getLocations())
    # for location in automaton.getLocations():
    #     print(automaton.getTransitions(source=location, method='I_push'))
    # print(automaton.outputs)


if __name__ == "__main__":
    main(sys.argv[1:])
