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
def add_galactic(graph, galactic_file):
    None

# Add thermal mirror emission to plot
def add_mirror(graph, mirror_temp, mirror_file):
    None

# Add zodiacal emission to plot
def add_zodiac(graph, zodiac_file):
    None

# Add cosmic infrared background to plot
def add_cib(graph):
    None

# Add cosmic microwave background to plot
def add_cmb(graph):
    None

# Add signal to plot
def add_signal(graph, site_file, source_file):
    None

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total noise to plot
def add_noise(graph, galactic_file, mirror_file, mirror_temp, zodiac_file, cib, cmb):
    None

# Add total temp to plot
def add_temp(graph, galactic_file, mirror_file, mirror_temp, zodiac_file,
        cib, cmb, aperture, site_file, source_file):
    None

# Add integration time to plot
def add_integ(graph, galactic_file, mirror_file, mirror_temp, zodiac_file,
        cib, cmb, aperture, site_file, source_file, snr):
    None
