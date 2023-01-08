from z3 import *
from xmlparser import ParsedXML
from generator.generate import generate


def main(argv):
    print(argv)
    try:
        if len(argv) == 0:
            raise ValueError
    except ValueError:
        print('missing xml input file')
        sys.exit(2)

    automaton = ParsedXML(argv)
    generate(automaton, 'I_push')


    # print(automaton.getLocations())
    # for location in automaton.getLocations():
    #     print(automaton.getTransitions(source=location, method='I_push'))
    # print(automaton.outputs)




if __name__ == "__main__":
    main(sys.argv[1])
