import sys
import xml.dom.minidom

from xmlparser import ParsedXML


def main(argv):
    print(argv)
    try:
        if len(argv) == 0:
            raise ValueError
    except (ValueError):
        print('missing xml input file')
        sys.exit(2)

    ParsedXML(argv)


if __name__ == "__main__":
    main(sys.argv[1])
