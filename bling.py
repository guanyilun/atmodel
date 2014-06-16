# bling.py
# generate lists of bling that can be plotted or further manipulated

import math
import numpy

import aux
import cal
import graph

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
    freq_list, temp_list = aux.get_col(file_name, "Hz", 0, "K", 0, freq_range)
    return cal.bling_sub(freq_list, temp_list, 1000), freq_list

# Atmospheric Radiance
def radiance(site_file, freq_range):
    
    # compute atmospheric radiance
    freq_list, radiance_list = aux.get_col(site_file, "Hz", 0, 0, "TOTAL RAD", freq_range)
    return cal.bling_AR(freq_list, radiance_list, 1000), freq_list

# Cosmic Microwave Background
def cmb(freq_range):
    
    # compute CMB noise for a set of frequencies
    freq_list, zero_list = aux.generate_freq(freq_range)
    return cal.bling_CMB(freq_list, 1000), freq_list

# Thermal Mirror Emission
def mirror(mirror_temp, constant, freq_range):
    
    # return array of zeros if mirror_temp and constant are both -1 (ie. not filled in)
    if mirror_temp == -1 or constant == -1:
        freq, zero = aux.generate_freq(freq_range)
        return zero, freq
    
    # compute thermal noise for a set of frequencies
    freq_list, zero_list = aux.generate_freq(freq_range)
    wavelengths = 299792458. / freq_list
    return cal.bling_TME(freq_list, 1000, constant, mirror_temp, wavelengths), freq_list

# total BLING noise
def noise_total(site_file, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, add_cib, add_cmb, freq_range):
    
    # compute all the individual noise sources if enough info provided
    if len(site_file) > 0:
        radiance_bsq, rfreq = radiance(site_file, freq_range)
    else:
        rfreq, radiance_bsq = aux.generate_freq(freq_range)
    
    if len(galactic_file) > 0:
        galactic_bsq, gfreq = generic_noise(galactic_file, freq_range)
    else:
        gfreq, galactic_bsq = aux.generate_freq(freq_range)
    
    if mirror_temp != -1 and mirror_constant != -1:
        mirror_bsq, mfreq = mirror(mirror_temp, mirror_constant, freq_range)
    else:
        mfreq, mirror_bsq = aux.generate_freq(freq_range)
    
    if len(zodiac_file) > 0:
        zodiac_bsq, zfreq = generic_noise(zodiac_file, freq_range)
    else:
        zfreq, zodiac_bsq = aux.generate_freq(freq_range)
    
    if add_cib == True:
        cib_bsq, cibfreq = generic_noise("data/Backgrounds/CIB/cib.xlsx", freq_range)
    else:
        cibfreq, cib_bsq = aux.generate_freq(freq_range)
    
    if add_cmb == True:
        cmb_bsq, cmbfreq = cmb(freq_range)
    else:
        cmbfreq, cmb_bsq = aux.generate_freq(freq_range)
    
    # combine the noise
    blingsq_tot = radiance_bsq + galactic_bsq + mirror_bsq + zodiac_bsq + cib_bsq + cmb_bsq
    return blingsq_tot, mfreq
    