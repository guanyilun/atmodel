# generate.py
# generate graph given inputs

from PyQt4 import QtCore, QtGui
from excel import ExcelXWriter, ExcelReader
import collections

import dyngui
import cal

name_file = collections.namedtuple("name_file", "name file")

# Add atmospheric radiance to plot
def add_radiance(graph, site_file):
    None

# Add atmospheric transmission to plot
def add_trans(graph, site_file):
    None

# Add galactic emission to plot
def add_galactic(graph, gcrd_file):
    None
