# generate.py
# generate graph given inputs

import collections
from excel import ExcelXWriter, ExcelReader
import math
import numpy
from PyQt4 import QtCore, QtGui

import dyngui
import cal
import graph

name_file = collections.namedtuple("name_file", "name file")
interval = collections.namedtuple("interval", "min max")

# Get column pair from data file
def get_col(file_name, col1, col1n, col2, col2n, freq_range):
    
    # read two columns from file and return them as numpy arrays
    data = ExcelReader(file_name)
    return [numpy.array(data.read_from_col(col1, freq_range.min, freq_range.max, col1n), dtype='float'),
        numpy.array(data.read_from_col(col2, freq_range.min, freq_range.max, col2n), dtype='float')]

# Build generic noise coordinate list
def generic_noise(file_name, freq_range):
    
    # compute noise from frequencies and temperatures
    freq_list, temp_list = get_col(file_name, "Hz", 0, "K", 0, freq_range)
    blingsq_list = cal.bling_sub(freq_list, temp_list, 1000)
    
    # build and return list of coordinates
    crdlist = []
    for i, bling_sq in enumerate(blingsq_list):
        crdlist.append(graph.coord_obj(freq_list[i], math.sqrt(bling_sq)))
    
    return crdlist

# Add atmospheric radiance to plot
def add_radiance(graph_obj, site_file, freq_range):
    
    # compute atmospheric radiance
    freq_list, radiance_list = get_col(site_file, "Hz", 0, 0, "TOTAL RAD", freq_range)
    blingsq_list = cal.bling_AR(freq_list, radiance_list, 1000)
    
    # convert noise into usable graph
    noise_list = []
    for i, bling_sq in enumerate(blingsq_list):
        noise_list.append(graph.coord_obj(freq_list[i], math.sqrt(bling_sq)))
    
    data_set = graph.data_set("Atmos Radiance", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(graph_obj, site_file, freq_range):
    None

# Add galactic emission to plot
def add_galactic(graph_obj, galactic_file, freq_range):
    noise_list = generic_noise(galactic_file, freq_range)
    data_set = graph.data_set("Galactic Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(graph_obj, mirror_temp, mirror_file, freq_range):
    None

# Add zodiacal emission to plot
def add_zodiac(graph_obj, zodiac_file, freq_range):
    noise_list = generic_noise(zodiac_file, freq_range)
    data_set = graph.data_set("Zodiacal Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# generate list of frequencies (in Hz) with identical form as data
def generate_freq(freq_range):
    step = 3e9 # increment (Hz)
    
    freq_min = 1.5e9 # minimum frequency
    freq_max = 1.64955e13 # maximum frequency
    if freq_range.min > freq_min:
        freq = int((freq_range.min - freq_min) / step + 1) * step + freq_min
    else: freq = freq_min
    
    freq_list = []
    while freq <= freq_range.max and freq <= freq_max:
        freq_list.append(freq)
        freq += step
    freq_array = numpy.array(freq_list, dtype="float")
    
    return freq_array

# Add cosmic infrared background to plot
def add_cib(graph_obj, freq_range):
    None

# Add cosmic microwave background to plot
def add_cmb(graph_obj, freq_range):
    
    # compute CMB noise for a set of frequencies
    freq_list = generate_freq(freq_range)
    blingsq_list = cal.bling_CMB(freq_list, 1000)
    
    # convert noise into usable graph
    noise_list = []
    for i, bling_sq in enumerate(blingsq_list):
        noise_list.append(graph.coord_obj(freq_list[i], math.sqrt(bling_sq)))
    
    data_set = graph.data_set("Cosmic Microwave Bkgd", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

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
