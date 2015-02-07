# bling.py
# generate lists of bling that can be plotted or further manipulated

import math
import numpy

import auxil as aux
import cal
import const
import graph

# Create noise list from bling squared list
def noise_list(gui, blingsq_list):

    # build and return list of coordinates
    crdlist = []

    if gui.bling_units == 0: # use W/Hz^1/2
        for i, bling_sq in enumerate(blingsq_list):
            crdlist.append(graph.coord_obj(gui.interp.freq_list[i], math.sqrt(bling_sq)))

    else: # use photons/s Hz^1/2
        for i, bling_sq in enumerate(blingsq_list):
            crdlist.append(graph.coord_obj(gui.interp.freq_list[i],
                    math.sqrt(bling_sq) / (const.h * gui.interp.freq_list[i])))

    return crdlist

# Build generic noise coordinate list
def generic_noise(gui, file_name, spec_res):

    # compute noise from frequencies and temperatures
    freq_raw, temp_raw = aux.get_col(file_name, "Hz", 0, "K", 0, gui.interp.freq_range)
    temp_list = gui.interp.interpolate(freq_raw.tolist(), temp_raw.tolist())
    return cal.bling_sub(numpy.array(gui.interp.freq_list), temp_list, spec_res)

# Atmospheric Radiance
def radiance(gui, site_file, spec_res):

    # compute atmospheric radiance
    freq_raw, radiance_raw = aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", gui.interp.freq_range)
    radiance_list = gui.interp.interpolate(freq_raw.tolist(), radiance_raw.tolist())
    return cal.bling_AR(numpy.array(gui.interp.freq_list),
        numpy.array(radiance_list), spec_res)

# Cosmic Microwave Background
def cmb(gui, spec_res):

    # compute CMB noise for a set of frequencies
    freq_list = numpy.array(gui.interp.freq_list)
    return cal.bling_CMB(freq_list, spec_res)

# Thermal Mirror Emission
def mirror(gui, mirror_temp, constant, spec_res):

    # return array of zeros if mirror_temp and constant are both -1 (ie. not filled in)
    if mirror_temp == -1 or constant == -1:
        zero = numpy.array(aux.get_zero(gui.interp.freq_list))
        return zero

    # compute thermal noise for a set of frequencies
    freq_list = numpy.array(gui.interp.freq_list)
    return cal.bling_TME(freq_list, spec_res, constant, mirror_temp)

# total BLING noise
def noise_total(gui, site_file, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, add_cib, add_cmb, spec_res):

    zero_array = numpy.array(aux.get_zero(gui.interp.freq_list))

    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        radiance_bsq = radiance(gui, site_file, spec_res)
    else:
        radiance_bsq = zero_array.copy()

    if len(galactic_file) > 0:
        galactic_bsq = generic_noise(gui, galactic_file, spec_res)
    else:
        galactic_bsq = zero_array.copy()

    if mirror_temp != -1 and mirror_constant != -1:
        mirror_bsq = mirror(gui, mirror_temp, mirror_constant, spec_res)
    else:
        mirror_bsq = zero_array.copy()

    if len(zodiac_file) > 0:
        zodiac_bsq = generic_noise(gui, zodiac_file, spec_res)
    else:
        zodiac_bsq = zero_array.copy()

    if add_cib == True:
        cib_bsq = generic_noise(gui, "data/Backgrounds/CIB/cib.xlsx", spec_res)
    else:
        cib_bsq = zero_array.copy()

    if add_cmb == True:
        cmb_bsq = cmb(gui, spec_res)
    else:
        cmb_bsq = zero_array.copy()

    # combine the noise
    blingsq_tot = radiance_bsq + galactic_bsq + mirror_bsq + zodiac_bsq + cib_bsq + cmb_bsq
    return blingsq_tot
