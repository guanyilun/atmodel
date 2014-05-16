# generate.py
# generate graph given inputs

from PyQt4 import QtCore, QtGui
from excel import ExcelXWriter, ExcelReader
import collections

import dyngui
import cal
import graph

name_file = collections.namedtuple("name_file", "name file")
interval = collections.namedtuple("interval", "min max")

# Build generic noise coordinate list
def generic_noise(file_name, freq_range):
    data = ExcelReader(file_name)
    
    # list of frequencies and galactic temperatures
    freq_list = np.array(data.read_from_col("Hz", freq_range.min, freq_range.max), dtype='float')
    temp_list = np.array(data.read_from_col("K", freq_range.min, freq_range.max), dtype='float')
    
    # compute noise from galaxy
    blingsq_list = cal.bling_sub(freq_list, temp_list, 1000)
    
    # build and return list of coord_obj
    crdlist = []
    for i, bling_sq in enumerate(blingsq_list):
        crdlist[i] = graph.coord_obj(freq_list[i], math.sqrt(bling_sq))
    
    return crdlist

# Add atmospheric radiance to plot
def add_radiance(graph_obj, site_file, freq_range):
    noise_list = generic_noise(site_file, freq_range)
    data_set = graph.data_set("Atmos Radiance", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj,dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(graph_obj, site_file, freq_range):
    None

# Add galactic emission to plot
def add_galactic(graph_obj, galactic_file, freq_range):
    noise_list = generic_noise(galactic_file, freq_range)
    data_set = graph.data_set("Galactic Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj,dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(graph_obj, mirror_temp, mirror_file, freq_range):
    None

# Add zodiacal emission to plot
def add_zodiac(graph_obj, zodiac_file, freq_range):
    noise_list = generic_noise(zodiac_file, freq_range)
    data_set = graph.data_set("Zodiacal Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj,dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(graph_obj, freq_range):
    None

# Add cosmic microwave background to plot
def add_cmb(graph_obj, freq_range):
    None

# Add signal to plot
def add_signal(graph_obj, site_file, source_file, freq_range):
    None

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total noise to plot
def add_noise(graph_obj, galactic_file, mirror_file, mirror_temp, zodiac_file, cib, cmb, freq_range):
    None

# Add total temp to plot
def add_temp(graph_obj, galactic_file, mirror_file, mirror_temp, zodiac_file,
        cib, cmb, aperture, site_file, source_file, freq_range):
    None

# Add integration time to plot
def add_integ(graph_obj, galactic_file, mirror_file, mirror_temp, zodiac_file,
        cib, cmb, aperture, site_file, source_file, snr, freq_range):
    None
