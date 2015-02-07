# temp.py
# generate lists of temperatures that can be plotted or further manipulated

import collections
from excel import ExcelXWriter, ExcelReader
import math
import numpy

import auxil as aux
import cal
import graph


# Create list of graph coordinates for temperature
def temp_list(gui, temp_array):

    # build and return list of coordinates
    crdlist = []
    for i, temp in enumerate(temp_array):
        crdlist.append(graph.coord_obj(gui.interp.freq_list[i], temp))

    return crdlist

# Build generic noise coordinate list
def generic_temp(gui, file_name):

    # compute noise from frequencies and temperatures
    freq_raw, temp_raw = aux.get_col(file_name, "Hz", 0, "K", 0, gui.interp.freq_range)
    temp_list = gui.interp.interpolate(freq_raw.tolist(), temp_raw.tolist())
    return numpy.array(temp_list)

# Atmospheric Radiance
def radiance(gui, site_file):

    # compute atmospheric radiance temperature
    freq_raw, radiance_raw = aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", gui.interp.freq_range)
    radiance_list = gui.interp.interpolate(freq_raw.tolist(), radiance_raw.tolist())
    return cal.temp_AR(numpy.array(gui.interp.freq_list), numpy.array(radiance_list))

# Cosmic Microwave Background
def cmb(gui):

    # compute CMB noise for a set of frequencies
    return cal.temp_CMB(numpy.array(gui.interp.freq_list))

# Thermal Mirror Emission
def mirror(gui, mirror_temp, constant):

    # return array of zeros if mirror_temp and constant are both -1 (ie. not filled in)
    if mirror_temp == -1 or constant == -1:
        zero = numpy.array(aux.get_zero(gui.interp.freq_list))
        return zero

    # compute thermal noise for a set of frequencies
    freq_list = numpy.array(gui.interp.freq_list)
    return cal.temp_TME(freq_list, constant, mirror_temp)

# total temperature
def total(gui, site_file, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, add_cib, add_cmb):

    zero_array = numpy.array(aux.get_zero(gui.interp.freq_list))

    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        radiance_temp = radiance(gui, site_file)
    else:
        radiance_temp = zero_array.copy()

    if len(galactic_file) > 0:
        galactic_temp = generic_temp(galactic_file)
    else:
        galactic_temp = zero_array.copy()

    if mirror_temp != -1 and mirror_constant != -1:
        mirror_temp = mirror(gui, mirror_temp, mirror_constant)
    else:
        mirror_temp = zero_array.copy()

    if len(zodiac_file) > 0:
        zodiac_temp = generic_temp(gui, zodiac_file)
    else:
        zodiac_temp = zero_array.copy()

    if add_cib == True:
        cib_temp = generic_temp(gui, "data/Backgrounds/CIB/cib.xlsx")
    else:
        cib_temp = zero_array.copy()

    if add_cmb == True:
        cmb_temp = cmb(gui)
    else:
        cmb_temp = zero_array.copy()

    # combine the noise
    temp_tot = radiance_temp + galactic_temp + mirror_temp + zodiac_temp + cib_temp + cmb_temp
    return temp_tot
