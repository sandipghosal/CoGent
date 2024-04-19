import xml.etree.ElementTree as ET

from errors import *
from import_xml.extract import extract


def import_ra(config):
    """ Import a register automaton from an input XML file """
    try:
        tree = ET.parse(config.PATH)
    except:
        InvalidInputFile('Invalid input file: ' + config.PATH)

    ra = extract(tree, config)

    return ra
