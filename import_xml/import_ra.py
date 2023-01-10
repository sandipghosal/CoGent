import xml.etree.ElementTree as ET
from import_xml.extract import extract


def import_ra(file):
    """ Import a register automaton from an input XML file """

    tree = ET.parse(file)
    return extract(tree)
    pass
