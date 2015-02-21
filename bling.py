# bling.py
# generate lists of bling that can be plotted or further manipulated

import math
import numpy as np

import auxil as aux
import cal
import const
import graph

# convert from BLING^2 to BLING
def convert (gui, blingsq):

    if gui.bling_units == 0: # already in W/Hz^1/2
        return np.sqrt(blingsq)

    elif gui.bling_units == 1: # convert to photons/s*Hz^1/2
        return np.sqrt(blingsq) / (const.h * gui.interp.freq_array)

# Build generic noise coordinate list
def generic (gui, file_name, spec_res):
    freq_raw, temp_raw = \
        aux.get_col(file_name, "Hz", 0, "K", 0, gui.interp.freq_range)
    temp_list = gui.interp.interpolate(freq_raw.tolist(), temp_raw.tolist())
    return convert(gui, cal.bling_sub(gui.interp.freq_array, temp_list, spec_res))

# Atmospheric Radiance
def radiance (gui, site_file, spec_res):
    freq_raw, radiance_raw = \
        aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", gui.interp.freq_range)
    radiance_list = gui.interp.interpolate(freq_raw.tolist(), radiance_raw.tolist())
    return convert(gui, cal.bling_AR(gui.interp.freq_array,
                                     np.array(radiance_list), spec_res))

# Cosmic Microwave Background
def cmb (gui, spec_res):
    return convert(gui, cal.bling_CMB(gui.interp.freq_array, spec_res))

# Thermal Mirror Emission
def mirror (gui, mirror_temp, constant, spec_res):
    return convert(gui, cal.bling_TME(gui.interp.freq_array, spec_res,
                                      constant, mirror_temp))

# total BLING noise
def noise_total(gui, site_file, galactic_file, mirror_temp, mirror_constant,
                zodiac_file, add_cib, add_cmb, spec_res):

    # start off with zero noise
    blingsq_tot = np.zeros(len(gui.interp.freq_list))

    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        blingsq_tot += radiance(gui, site_file, spec_res)

    if len(galactic_file) > 0:
        blingsq_tot += generic(gui, galactic_file, spec_res)

    if mirror_temp != -1 and mirror_constant != -1:
        blingsq_tot += mirror(gui, mirror_temp, mirror_constant, spec_res)

    if len(zodiac_file) > 0:
        blingsq_tot += generic(gui, zodiac_file, spec_res)

    if add_cib == True:
        blingsq_tot += generic(gui, "data/Backgrounds/CIB/cib.xlsx", spec_res)

    if add_cmb == True:
        blingsq_tot += cal.bling_CMB(freq_list, spec_res)

    return convert(gui, blingsq_tot)
