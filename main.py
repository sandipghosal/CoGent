import datetime
import getopt
from customlogger.logging import CustomFormatter
import os

from errors import *
from generator import generate
from import_xml import import_ra


def setuplogger(switch, logfile, loglevel=None):
    logger = logging.getLogger("CoGent")
    if switch:
        logpath = 'log'
        exist = os.path.exists(logpath)
        # if log directory does not exist create one
        if not exist:
            os.makedirs(logpath)

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
    else:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


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
                print('python main.py -i <XML file> -t <Target Method> -l <Log file> -g <DEBUG|ERROR|WARNING>')
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
                          "DEBUG": logging.DEBUG,
                          "WARNING": logging.WARNING,
                          }
                level = levels.get(option, logging.NOTSET)

    except (ValueError, getopt.GetoptError):
        print('python main.py -h [--help]')
        sys.exit(2)

    # set up the logging environment
    setuplogger(switch=logswitch, logfile=logfile, loglevel=level)

    # check if user has provided the XML file
    try:
        if not xmlfile:
            raise InputsNotFound('XML file not found')
        elif not target:
            raise InputsNotFound('Target method not found')
        else:
            logging.debug('input XML file path:' + xmlfile)
    except (InputsNotFound, getopt.GetoptError):
        print('python main.py -h [--help]')
        sys.exit(2)

    logging.debug('target method:' + target)
    # import the automaton from the XML file
    automaton = import_ra(xmlfile)
    generate(automaton, target)

    # print(automaton.getLocations())
    # for location in automaton.getLocations():
    #     print(automaton.getTransitions(source=location, method='I_push'))
    # print(automaton.outputs)


if __name__ == "__main__":
    main(sys.argv[1:])
