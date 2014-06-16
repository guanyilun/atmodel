# generate.py
# generate graph given inputs

import math
import numpy

import bling
import cal
import dyngui
import graph
import sigtrans
import temp

# Create data set with proper photon energy type and units
def new_dataset(label, energy_form, dep_type, dep_units, data_hz):
    
    # build new set of coordinates with proper photon energy form
    crdlist = []
    for hz_crd in data_hz:
        crdlist.append(graph.coord_obj(energy_form.from_hz(hz_crd.x), hz_crd.y))
    
    return graph.data_set(label, energy_form.type, energy_form.units, dep_type, dep_units, crdlist)

# Add atmospheric radiance to plot
def add_radiance(gui, graph_obj, site_file):
    noise_list = bling.noise_list(*bling.radiance(site_file.file, gui.freq_range))
    data_set = new_dataset("Atmos Radiance ("+site_file.name+")", gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(gui, graph_obj, site_file):
    trans_list, freq_list = sigtrans.trans(site_file.file, gui.freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, trans_val in enumerate(trans_list):
        crdlist.append(graph.coord_obj(freq_list[i], trans_val))
    
    # build data set and add to graph
    data_set = new_dataset("Atmos Trans ("+site_file.name+")", gui.energy_form, "Transmission", "Proportion", crdlist)
    graph_obj.dataset_list.append(data_set)

# Add galactic emission to plot
def add_galactic(gui, graph_obj, galactic_file):
    noise_list = bling.noise_list(*bling.generic_noise(galactic_file.file, gui.freq_range))
    data_set = new_dataset("Galactic Emission ("+galactic_file.name+")",
            gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(gui, graph_obj, metal_name, mirror_temp, constant):
    noise_list = bling.noise_list(*bling.mirror(mirror_temp, constant, gui.freq_range))
    data_set = new_dataset("Thermal Mirror ("+metal_name+", "+str(mirror_temp)+" K)",
            gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add zodiacal emission to plot
def add_zodiac(gui, graph_obj, zodiac_file):
    noise_list = bling.noise_list(*bling.generic_noise(zodiac_file.file, gui.freq_range))
    data_set = new_dataset("Zodiacal Emission ("+zodiac_file.name+")",
            gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(gui, graph_obj):
    # TODO: convert to equation fit
    noise_list = bling.noise_list(*bling.generic_noise("data/Backgrounds/CIB/cib.xlsx", gui.freq_range))
    data_set = new_dataset("Cosmic Infrared Bkgd", gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic microwave background to plot
def add_cmb(gui, graph_obj):
    noise_list = bling.noise_list(*bling.cmb(gui.freq_range))
    data_set = new_dataset("Cosmic Microwave Bkgd", gui.energy_form, "BLING", "W/Hz$^{1/2}$", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add signal to plot
def add_signal(gui, graph_obj, aperture, site_file, source_file):
    sig_list, freq_list = sigtrans.signal(aperture, site_file.file, source_file.file, gui.freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, signal_val in enumerate(sig_list):
        crdlist.append(graph.coord_obj(freq_list[i], signal_val))
    
    # build data set and add to graph
    data_set = new_dataset("Signal ("+str(aperture)+" m, "+site_file.name+", "+source_file.name+")",
            gui.energy_form, "Signal", "W", crdlist)
    graph_obj.dataset_list.append(data_set)

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total noise to plot
def add_noise(gui, graph_obj, label, site_file, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb):
    
    blingsq_tot, mfreq = bling.noise_total(site_file.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, gui.freq_range)
    data_set = new_dataset("Total Noise ("+label+")", gui.energy_form, "BLING", "W/Hz$^{1/2}$",
            bling.noise_list(blingsq_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add total temp to plot
def add_temp(gui, graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file):
    
    if len(site_file.file) > 0:
        site = site_file.file
    elif len(atmos_site.file) > 0:
        site = atmos_site.file
    
    temp_tot, mfreq = temp.total(site, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, gui.freq_range)
    data_set = new_dataset("Total Temp ("+label+")", gui.energy_form, "Temperature", "K",
            temp.temp_list(temp_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add integration time to plot
def add_integ(gui, graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, snr):
    
    # compute noise and signal and, with signal:noise ratio, integration time
    blingsq_tot, mfreq = bling.noise_total(atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, gui.freq_range)
    sig_list, slist = sigtrans.signal(aperture, site_file.file, source_file.file, gui.freq_range)
    integ_time = cal.IT(blingsq_tot, snr, sig_list) # array of integration times
    
    # build and return list of coordinates
    crdlist = []
    for i, integ_val in enumerate(integ_time):
        crdlist.append(graph.coord_obj(mfreq[i], integ_val))
    
    # build data set and add to graph
    data_set = new_dataset("Integration Time ("+label+")", gui.energy_form, "Time", "s", crdlist)
    graph_obj.dataset_list.append(data_set)
