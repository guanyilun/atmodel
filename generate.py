# generate.py
# generate graph given inputs

import math
import numpy

import dyngui
import graph
import plotdata

# Add atmospheric radiance to plot
def add_radiance(graph_obj, site_file, freq_range):
    noise_list = plotdata.radiance(site_file, freq_range)
    data_set = graph.data_set("Atmos Radiance", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(graph_obj, site_file, freq_range):
    None

# Add galactic emission to plot
def add_galactic(graph_obj, galactic_file, freq_range):
    noise_list = plotdata.generic_noise(galactic_file, freq_range)
    data_set = graph.data_set("Galactic Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(graph_obj, mirror_temp, constant, freq_range):
    freq_list = generate_freq(freq_range)

# Add zodiacal emission to plot
def add_zodiac(graph_obj, zodiac_file, freq_range):
    noise_list = plotdata.generic_noise(zodiac_file, freq_range)
    data_set = graph.data_set("Zodiacal Emission", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(graph_obj, freq_range):
    None

# Add cosmic microwave background to plot
def add_cmb(graph_obj, freq_range):
    noise_list = plotdata.cmb(freq_range)
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
