import logging
from pprint import pp
import xml.etree.ElementTree as ET
from import_xml.extract import extract
from errors import *


def import_ra(file):
    """ Import a register automaton from an input XML file """
    try:
        tree = ET.parse(file)
    except:
        InvalidInputFile('Invalid input file: ' + file)
    return extract(tree)
