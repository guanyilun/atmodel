# generate.py
# generate graph given inputs

import math
import numpy

import bling
import cal
import dyngui
import graph
import sigtrans

# Add atmospheric radiance to plot
def add_radiance(graph_obj, site_file, freq_range):
    noise_list = bling.noise_list(*bling.radiance(site_file.file, freq_range))
    data_set = graph.data_set("Atmos Radiance ("+site_file.name+")", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(graph_obj, site_file, freq_range):
    None

# Add galactic emission to plot
def add_galactic(graph_obj, galactic_file, freq_range):
    noise_list = bling.noise_list(*bling.generic_noise(galactic_file.file, freq_range))
    data_set = graph.data_set("Galactic Emission ("+galactic_file.name+")",
            "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(graph_obj, metal_name, mirror_temp, constant, freq_range):
    noise_list = bling.noise_list(*bling.mirror(mirror_temp, constant, freq_range))
    data_set = graph.data_set("Thermal Mirror ("+metal_name+", "+mirror_temp+" K)",
            "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add zodiacal emission to plot
def add_zodiac(graph_obj, zodiac_file, freq_range):
    noise_list = bling.noise_list(*bling.generic_noise(zodiac_file.file, freq_range))
    data_set = graph.data_set("Zodiacal Emission ("+zodiac_file.file+")", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(graph_obj, freq_range):
    # TODO: convert to equation fit
    noise_list = bling.noise_list(*bling.generic_noise("data/Backgrounds/CIB/cib.xlsx", freq_range))
    data_set = graph.data_set("Cosmic Infrared Bkgd", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic microwave background to plot
def add_cmb(graph_obj, freq_range):
    noise_list = bling.noise_list(*bling.cmb(freq_range))
    data_set = graph.data_set("Cosmic Microwave Bkgd", "Frequency", "Hz", "Noise", "BLING", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add signal to plot
def add_signal(graph_obj, aperture, site_file, source_file, freq_range):
    sig_list, freq_list = sigtrans.signal(aperture, site_file.file, source_file.file, freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, signal_val in enumerate(sig_list):
        crdlist.append(graph.coord_obj(freq_list[i], signal_val))
    
    # build data set and add to graph
    data_set = graph.data_set("Signal ("+site_file.name+", "+source_file.name+")",
            "Frequency", "Hz", "Signal", "W", crdlist)
    graph_obj.dataset_list.append(data_set)

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total noise to plot
def add_noise(graph_obj, label, site_file, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb, freq_range):
    
    blingsq_tot, mfreq = bling.noise_total(site_file.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, freq_range)
    data_set = graph.data_set("Total Noise ("+label+")", "Frequency", "Hz", "Noise", "BLING",
            bling.noise_list(blingsq_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add total temp to plot
def add_temp(graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, freq_range):
    None

# Add integration time to plot
def add_integ(graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, snr, freq_range):
    
    # compute noise and signal and, with signal:noise ratio, integration time
    blingsq_tot, mfreq = bling.noise_total(atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, freq_range)
    sig_list, slist = sigtrans.signal(aperture, site_file.file, source_file.file, freq_range)
    integ_time = cal.IT(blingsq_tot, snr, sig_list) # array of integration times
    
    # build and return list of coordinates
    crdlist = []
    for i, integ_val in enumerate(integ_time):
        crdlist.append(graph.coord_obj(mfreq[i], integ_val))
    
    # build data set and add to graph
    data_set = graph.data_set("Integration Time ("+label+")", "Frequency", "Hz", "Time", "s", crdlist)
    graph_obj.dataset_list.append(data_set)
