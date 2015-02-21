# temp.py
# generate lists of temperatures that can be plotted or further manipulated

import collections
from excel import ExcelXWriter, ExcelReader
import math
import numpy as np

import auxil as aux
import cal
import graph

# Build generic noise coordinate list
def generic (gui, file_name):
    freq_raw, temp_raw = aux.get_col(file_name, "Hz", 0, "K", 0, gui.interp.freq_range)
    temp_list = gui.interp.interpolate(freq_raw.tolist(), temp_raw.tolist())
    return np.array(temp_list)

# Atmospheric Radiance
def radiance (gui, site_file):
    freq_raw, radiance_raw = aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", gui.interp.freq_range)
    radiance_list = gui.interp.interpolate(freq_raw.tolist(), radiance_raw.tolist())
    return cal.temp_AR(gui.interp.freq_array, np.array(radiance_list))

# Cosmic Microwave Background
def cmb (gui):
    return cal.temp_CMB(gui.interp.freq_array)

# Thermal Mirror Emission
def mirror (gui, mirror_temp, constant):
    return cal.temp_TME(gui.interp.freq_array, constant, mirror_temp)

# total temperature
def total (gui, site_file, galactic_file, mirror_temp, mirror_constant,
           zodiac_file, add_cib, add_cmb):

    temp_tot = np.zeros(len(gui.interp.freq_list))

    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        temp_tot += radiance(gui, site_file)

    if len(galactic_file) > 0:
        temp_tot += generic(galactic_file)

    if mirror_temp != -1 and mirror_constant != -1:
        temp_tot += mirror(gui, mirror_temp, mirror_constant)

    if len(zodiac_file) > 0:
        temp_tot += generic(gui, zodiac_file)

    if add_cib == True:
        temp_tot += generic(gui, "data/Backgrounds/CIB/cib.xlsx")

    if add_cmb == True:
        temp_tot += cmb(gui)

    return temp_tot
