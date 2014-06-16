# temp.py
# generate lists of temperatures that can be plotted or further manipulated

import collections
from excel import ExcelXWriter, ExcelReader
import math
import numpy

import aux
import cal
import graph
    

# Create list of graph coordinates for temperature
def temp_list(temp_array, freq_list):
    
    # build and return list of coordinates
    crdlist = []
    for i, temp in enumerate(temp_array):
        crdlist.append(graph.coord_obj(freq_list[i], temp))
    
    return crdlist

# Build generic noise coordinate list
def generic_temp(file_name, freq_range):
    
    # compute noise from frequencies and temperatures
    freq_list, temp_list = aux.get_col(file_name, "Hz", 0, "K", 0, freq_range)
    return temp_list, freq_list

# Atmospheric Radiance
def radiance(site_file, freq_range):
    
    # compute atmospheric radiance temperature
    freq_list, radiance_list = aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", freq_range)
    return cal.temp_AR(freq_list, radiance_list), freq_list

# Cosmic Microwave Background
def cmb(freq_range):
    
    # compute CMB noise for a set of frequencies
    freq_list, zero_list = aux.generate_freq(freq_range)
    return cal.temp_CMB(freq_list), freq_list

# Thermal Mirror Emission
def mirror(mirror_temp, constant, freq_range):
    
    # return array of zeros if mirror_temp and constant are both -1 (ie. not filled in)
    if mirror_temp == -1 or constant == -1:
        freq, zero = aux.generate_freq(freq_range)
        return zero, freq
    
    # compute thermal noise for a set of frequencies
    freq_list, zero_list = aux.generate_freq(freq_range)
    wavelengths = 299792458. / freq_list
    return cal.temp_TME(freq_list, 1000, constant, mirror_temp, wavelengths), freq_list

# total temperature
def total(site_file, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, add_cib, add_cmb, freq_range):
    
    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        radiance_temp, rfreq = radiance(site_file, freq_range)
    else:
        rfreq, radiance_temp = aux.generate_freq(freq_range)
    
    if len(galactic_file) > 0:
        galactic_temp, gfreq = generic_temp(galactic_file, freq_range)
    else:
        gfreq, galactic_temp = aux.generate_freq(freq_range)
    
    if mirror_temp != -1 and mirror_constant != -1:
        mirror_temp, mfreq = mirror(mirror_temp, mirror_constant, freq_range)
    else:
        mfreq, mirror_temp = aux.generate_freq(freq_range)
    
    if len(zodiac_file) > 0:
        zodiac_temp, zfreq = generic_temp(zodiac_file, freq_range)
    else:
        zfreq, zodiac_temp = aux.generate_freq(freq_range)
    
    if add_cib == True:
        cib_temp, cibfreq = generic_temp("data/Backgrounds/CIB/cib.xlsx", freq_range)
    else:
        cibfreq, cib_temp = aux.generate_freq(freq_range)
    
    if add_cmb == True:
        cmb_temp, cmbfreq = cmb(freq_range)
    else:
        cmbfreq, cmb_temp = aux.generate_freq(freq_range)
    
    # combine the noise
    temp_tot = radiance_temp + galactic_temp + mirror_temp + zodiac_temp + cib_temp + cmb_temp
    return temp_tot, mfreq
    