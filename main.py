import datetime
import getopt
import time


import os
import ramodel.config
from errors import *
from generator import generate


def setuplogger(switch, logfile_, loglevel=logging.DEBUG):
    # logger_name = inspect.stack()[1][3]
    # logger = logging.getLogger(logger_name)
    if switch:
        logpath = 'log'
        exist = os.path.exists(logpath)
        # if log directory does not exist create one
        if not exist:
            os.makedirs(logpath)

        if logfile_ is None:
            # create a default log file using the timestamp
            logfile = 'log/' + str(datetime.datetime.now()).split(' ')[1] + '.log'
        else:
            logfile = logfile_

        print('log file created:' + logfile)
        logging.basicConfig(filename=logfile, filemode='w', level=loglevel,
                            format="%(name)s - %(levelname)s : %(message)s")
        # fhandler = logging.FileHandler(logfile)
        # fhandler.setLevel(loglevel)
        # fhandler.setFormatter(CustomFormatter())
        # logger.addHandler(fhandler)
    else:
        logging.basicConfig(stream=sys.stdout, filemode='w', level=loglevel,
                            format="%(name)s - %(levelname)s : %(message)s")
        # chandler = logging.StreamHandler()
        # chandler.setLevel(logging.DEBUG)
        # chandler.setFormatter(CustomFormatter())
        # logger.addHandler(chandler)

    # return logger


def main(argv):
    try:
        if len(argv) == 0:
            raise ValueError()

        options, arguments = getopt.getopt(sys.argv[1:],
                                           "hi:t:a:l:g:",
                                           ["help",
                                            "input=",
                                            "target=",
                                            "axioms=",
                                            "log=",
                                            "log-level="])

        xmlfile = target = afile = logfile = None
        logswitch = False
        level = logging.DEBUG

        for option, argument in options:
            if option in ("-h", "--help"):
                print('python main.py -i <XML file> -t <Target Method> -a <Axioms file> -l <Log file> -g <DEBUG|ERROR|WARNING>')
                sys.exit()

            elif option in ("-i", "--input"):
                xmlfile = argument

            elif option in ("-t", "--target"):
                target = argument

            elif option in ("-a", "--axioms"):
                afile = argument

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
    setuplogger(switch=logswitch, logfile_=logfile, loglevel=level)

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
    # automaton = import_ra(xmlfile)
    config = ramodel.Config(xmlfile)
    config.config(target, afile)
    start = time.time()
    generate(config)
    end = time.time()
    logging.debug('\n')
    logging.debug('\nTime taken for synthesis:' + str(end - start) + 'sec')

    print('\nTime taken for synthesis:' + str(end - start) + 'sec')

    print('\nContract Synthesis Completed')

    # print(automaton.getLocations())
    # for location in automaton.getLocations():
    #     print(automaton.getTransitions(source=location, method='I_push'))
    # print(automaton.outputs)


if __name__ == "__main__":
    main(sys.argv[1:])
