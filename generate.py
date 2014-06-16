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
def add_radiance(graph_obj, energy_form, site_file, freq_range):
    noise_list = bling.noise_list(*bling.radiance(site_file.file, freq_range))
    data_set = new_dataset("Atmos Radiance ("+site_file.name+")", energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(graph_obj, energy_form, site_file, freq_range):
    trans_list, freq_list = sigtrans.trans(site_file.file, freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, trans_val in enumerate(trans_list):
        crdlist.append(graph.coord_obj(freq_list[i], trans_val))
    
    # build data set and add to graph
    data_set = new_dataset("Atmos Trans ("+site_file.name+")", energy_form, "Transmission", "Proportion", crdlist)
    graph_obj.dataset_list.append(data_set)

# Add galactic emission to plot
def add_galactic(graph_obj, energy_form, galactic_file, freq_range):
    noise_list = bling.noise_list(*bling.generic_noise(galactic_file.file, freq_range))
    data_set = new_dataset("Galactic Emission ("+galactic_file.name+")",
            energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(graph_obj, energy_form, metal_name, mirror_temp, constant, freq_range):
    noise_list = bling.noise_list(*bling.mirror(mirror_temp, constant, freq_range))
    data_set = new_dataset("Thermal Mirror ("+metal_name+", "+str(mirror_temp)+" K)",
            energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add zodiacal emission to plot
def add_zodiac(graph_obj, energy_form, zodiac_file, freq_range):
    noise_list = bling.noise_list(*bling.generic_noise(zodiac_file.file, freq_range))
    data_set = new_dataset("Zodiacal Emission ("+zodiac_file.name+")",
            energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(graph_obj, energy_form, freq_range):
    # TODO: convert to equation fit
    noise_list = bling.noise_list(*bling.generic_noise("data/Backgrounds/CIB/cib.xlsx", freq_range))
    data_set = new_dataset("Cosmic Infrared Bkgd", energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add cosmic microwave background to plot
def add_cmb(graph_obj, energy_form, freq_range):
    noise_list = bling.noise_list(*bling.cmb(freq_range))
    data_set = new_dataset("Cosmic Microwave Bkgd", energy_form, "Noise", "W/Hz^0.5", noise_list)
    graph_obj.dataset_list.append(data_set)

# Add signal to plot
def add_signal(graph_obj, energy_form, aperture, site_file, source_file, freq_range):
    sig_list, freq_list = sigtrans.signal(aperture, site_file.file, source_file.file, freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, signal_val in enumerate(sig_list):
        crdlist.append(graph.coord_obj(freq_list[i], signal_val))
    
    # build data set and add to graph
    data_set = new_dataset("Signal ("+str(aperture)+" m, "+site_file.name+", "+source_file.name+")",
            energy_form, "Signal", "W", crdlist)
    graph_obj.dataset_list.append(data_set)

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total noise to plot
def add_noise(graph_obj, energy_form, label, site_file, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb, freq_range):
    
    blingsq_tot, mfreq = bling.noise_total(site_file.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, freq_range)
    data_set = new_dataset("Total Noise ("+label+")", energy_form, "Noise", "W/Hz^0.5",
            bling.noise_list(blingsq_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add total temp to plot
def add_temp(graph_obj, energy_form, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, freq_range):
    
    if len(site_file.file) > 0:
        site = site_file.file
    elif len(atmos_site.file) > 0:
        site = atmos_site.file
    
    temp_tot, mfreq = temp.total(site, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, freq_range)
    data_set = new_dataset("Total Temp ("+label+")", energy_form, "Temperature", "K",
            temp.temp_list(temp_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add integration time to plot
def add_integ(graph_obj, energy_form, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
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
    data_set = new_dataset("Integration Time ("+label+")", energy_form, "Time", "s", crdlist)
    graph_obj.dataset_list.append(data_set)
