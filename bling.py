# bling.py
# generate lists of bling that can be plotted or further manipulated

import collections
from excel import ExcelXWriter, ExcelReader
import math
import numpy

import cal
import graph

name_file = collections.namedtuple("name_file", "name file")
interval = collections.namedtuple("interval", "min max")

# Get column pair from data file
def get_col(file_name, col1, col1n, col2, col2n, freq_range):
    
    try:
        # read two columns from file and return them as numpy arrays
        data = ExcelReader(file_name)
        return [numpy.array(data.read_from_col(col1, freq_range.min, freq_range.max, col1n), dtype='float'),
            numpy.array(data.read_from_col(col2, freq_range.min, freq_range.max, col2n), dtype='float')]
    except Exception:
        # return blank data
        return [numpy.array([]), numpy.array([])]

# generate list of frequencies (in Hz) with identical form as data
def generate_freq(freq_range):
    step = 3e9 # increment (Hz)
    
    freq_min = 1.5e9 # minimum frequency
    freq_max = 1.64955e13 # maximum frequency
    if freq_range.min > freq_min:
        freq = int((freq_range.min - freq_min) / step + 1) * step + freq_min
    else: freq = freq_min
    
    freq_list = []
    while freq < freq_range.max - 1e-5 and freq < freq_max - 1e-5:
        freq_list.append(freq)
        freq += step
    freq_array = numpy.array(freq_list, dtype="float")
    
    return freq_array

# Create noise list from bling squared list
def noise_list(blingsq_list, freq_list):
    
    # build and return list of coordinates
    crdlist = []
    for i, bling_sq in enumerate(blingsq_list):
        crdlist.append(graph.coord_obj(freq_list[i], math.sqrt(bling_sq)))
    
    return crdlist

# Build generic noise coordinate list
def generic_noise(file_name, freq_range):
    
    # compute noise from frequencies and temperatures
    freq_list, temp_list = get_col(file_name, "Hz", 0, "K", 0, freq_range)
    return cal.bling_sub(freq_list, temp_list, 1000), freq_list

# Atmospheric Radiance
def radiance(site_file, freq_range):
    
    # compute atmospheric radiance
    freq_list, radiance_list = get_col(site_file, "Hz", 0, 0, "TOTAL RAD", freq_range)
    return cal.bling_AR(freq_list, radiance_list, 1000), freq_list

# Cosmic Microwave Background
def cmb(freq_range):
    
    # compute CMB noise for a set of frequencies
    freq_list = generate_freq(freq_range)
    return cal.bling_CMB(freq_list, 1000), freq_list

# Thermal Mirror Emission
def mirror(mirror_temp, constant, freq_range):
    
    # compute thermal noise for a set of frequencies
    freq_list = generate_freq(freq_range)
    wavelengths = 299792458. / freq_list
    return cal.bling_TME(freq_list, 1000, constant, mirror_temp, wavelengths), freq_list

# total BLING noise
def noise_total(site_file, galactic_file, mirror_file, mirror_temp,
        mirror_constant, zodiac_file, add_cib, add_cmb, freq_range):
    
    # compute all the individual noise sources
    radiance_bsq, rfreq = radiance(site_file, freq_range)
    galactic_bsq, gfreq = generic_noise(galactic_file, freq_range)
    mirror_bsq, mfreq = mirror(mirror_temp, mirror_constant, freq_range)
    zodiac_bsq, zfreq = generic_noise(zodiac_file, freq_range)
    cib_bsq, cibfreq = generic_noise("data/Backgrounds/CIB/cib.xlsx", freq_range)
    cmb_bsq, cmbfreq = cmb(freq_range)
    
    # combine the noise
    blingsq_tot = radiance_bsq + galactic_bsq + mirror_bsq + zodiac_bsq + cib_bsq + cmb_bsq
    return blingsq_tot, mfreq
    