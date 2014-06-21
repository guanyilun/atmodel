# py
# generate graph given inputs

import math
import numpy

import bling
import cal
import dyngui
import graph
import sigtrans
import temp

# Return selected units of BLING
def bling_units(gui):
    if gui.bling_units == 0:
        return "W/Hz$^{1/2}$"
    else:
        return "photons/s$\cdot$Hz$^{1/2}$"

# Create data set with proper photon energy type and units
def new_dataset(label, energy_form, dep_type, dep_units, data_hz):
    
    # build new set of coordinates with proper photon energy form
    crdlist = []
    for hz_crd in data_hz:
        crdlist.append(graph.coord_obj(energy_form.from_hz(hz_crd.x), hz_crd.y))
    
    return graph.data_set(label, energy_form.type, energy_form.units, dep_type, dep_units, crdlist)

# Add atmospheric radiance to plot
def add_radiance(gui, graph_obj, site_file, spec_res):
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.radiance(site_file.file, spec_res, gui.freq_range))
        data_set = new_dataset("Atmos Radiance ("+site_file.name+")", gui.energy_form,
                "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.radiance(site_file.file, gui.freq_range))
        data_set = new_dataset("Atmos Radiance ("+site_file.name+")", gui.energy_form,
                "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans(gui, graph_obj, site_file, spec_res):
    trans_list, freq_list = sigtrans.trans(site_file.file, gui.freq_range)
    
    # build and return list of coordinates
    crdlist = []
    for i, trans_val in enumerate(trans_list):
        crdlist.append(graph.coord_obj(freq_list[i], trans_val))
    
    # build data set and add to graph
    data_set = new_dataset("Atmos Trans ("+site_file.name+")", gui.energy_form,
            "Transmission", "Proportion", crdlist)
    graph_obj.dataset_list.append(data_set)

# Add galactic emission to plot
def add_galactic(gui, graph_obj, galactic_file, spec_res):
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.generic_noise(galactic_file.file, spec_res, gui.freq_range))
        data_set = new_dataset("Galactic Emission ("+galactic_file.name+")",
                gui.energy_form, "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.generic_temp(galactic_file.file, gui.freq_range))
        data_set = new_dataset("Galactic Emission ("+galactic_file.name+")",
                gui.energy_form, "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror(gui, graph_obj, metal_name, mirror_temp, constant, spec_res):
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.mirror(mirror_temp, constant, spec_res, gui.freq_range))
        data_set = new_dataset("Thermal Mirror ("+metal_name+", "+str(mirror_temp)+" K)",
                gui.energy_form, "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.mirror(mirror_temp, constant, gui.freq_range))
        data_set = new_dataset("Thermal Mirror ("+metal_name+", "+str(mirror_temp)+" K)",
                gui.energy_form, "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add zodiacal emission to plot
def add_zodiac(gui, graph_obj, zodiac_file, spec_res):
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.generic_noise(zodiac_file.file, spec_res, gui.freq_range))
        data_set = new_dataset("Zodiacal Emission ("+zodiac_file.name+")",
                gui.energy_form, "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.generic_temp(zodiac_file.file, gui.freq_range))
        data_set = new_dataset("Zodiacal Emission ("+zodiac_file.name+")",
                gui.energy_form, "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib(gui, graph_obj, spec_res):
    # TODO: convert to equation fit
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.generic_noise("data/Backgrounds/CIB/cib.xlsx", spec_res, gui.freq_range))
        data_set = new_dataset("Cosmic Infrared Bkgd", gui.energy_form, "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.generic_temp("data/Backgrounds/CIB/cib.xlsx", gui.freq_range))
        data_set = new_dataset("Cosmic Infrared Bkgd", gui.energy_form, "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add cosmic microwave background to plot
def add_cmb(gui, graph_obj, spec_res):
    
    if gui.noise_what == 0: # BLING
        noise_list = bling.noise_list(gui, *bling.cmb(spec_res, gui.freq_range))
        data_set = new_dataset("Cosmic Microwave Bkgd", gui.energy_form, "BLING", bling_units(gui), noise_list)
    else: # temperature
        temp_list = temp.temp_list(*temp.cmb(gui.freq_range))
        data_set = new_dataset("Cosmic Microwave Bkgd", gui.energy_form, "Temperature", "K", temp_list)
    
    graph_obj.dataset_list.append(data_set)

# Add signal to plot
def add_signal(gui, graph_obj, aperture, site_file, source_file, spec_res):
    sig_list, freq_list = sigtrans.signal(aperture, site_file.file, source_file.file, spec_res, gui.freq_range)
    
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
        mirror_constant, zodiac_file, cib, cmb, spec_res):
    
    blingsq_tot, mfreq = bling.noise_total(site_file.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, spec_res, gui.freq_range)
    data_set = new_dataset("Total Noise ("+label+")", gui.energy_form, "BLING", bling_units(gui),
            bling.noise_list(gui, blingsq_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add total temp to plot
def add_temp(gui, graph_obj, label, atmos_site, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb):
    
    temp_tot, mfreq = temp.total(site, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, gui.freq_range)
    data_set = new_dataset("Total Temp ("+label+")", gui.energy_form, "Temperature", "K",
            temp.temp_list(temp_tot, mfreq))
    graph_obj.dataset_list.append(data_set)

# Add integration time to plot
def add_integ(gui, graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, snr, spec_res):
    
    # compute noise and signal and, with signal:noise ratio, integration time
    blingsq_tot, mfreq = bling.noise_total(atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, spec_res, gui.freq_range)
    sig_list, slist = sigtrans.signal(aperture, site_file.file, source_file.file, spec_res, gui.freq_range)
    integ_time = cal.IT(blingsq_tot, snr, sig_list) # array of integration times
    
    # build and return list of coordinates
    crdlist = []
    for i, integ_val in enumerate(integ_time):
        crdlist.append(graph.coord_obj(mfreq[i], integ_val))
    
    # build data set and add to graph
    data_set = new_dataset("Integration Time ("+label+")", gui.energy_form, "Time", "s", crdlist)
    graph_obj.dataset_list.append(data_set)

# generate a graph with inputs
def process(gui):
    
    new_graph = graph.graph_obj(gui.config_sets[0]["name"].widget.text(), [])
    gui.energy_form = gui.energy_list[gui.config_sets[1]["e_units"].widget.currentIndex()]
    
    try:
        noise_res = float(gui.noise_res.text())
    except Exception:
        noise_res = config.spec_res
    
    # Atmospheric radiance
    if gui.atmos_toplot[0].isChecked():
        # loop through all selected sites
        for group in gui.atmos_collection:
            index = group.inputs["site"].widget.currentIndex()
            # only add to graph if a site is selected
            if index > 0:
                add_radiance(gui, new_graph, gui.atmos_files[index - 1], noise_res)
    
    # Atmospheric transmission
    if gui.atmos_toplot[1].isChecked():
        # loop through all selected sites
        for group in gui.atmos_collection:
            index = group.inputs["site"].widget.currentIndex()
            # only add to graph if a site is selected
            if index > 0:
                add_trans(gui, new_graph, gui.atmos_files[index - 1])
    
    # Galactic emission
    if gui.galactic_toplot.isChecked():
        # loop through all selected coordinates
        for group in gui.galactic_collection:
            index = group.inputs["gcrd"].widget.currentIndex()
            # only add to graph if a coordinate is selected
            if index > 0:
                add_galactic(gui, new_graph, gui.galactic_files[index - 1], noise_res)
    
    # Thermal mirror emission
    if gui.mirror_toplot.isChecked():
        # loop through all selected mirror types
        for group in gui.mirror_collection:
            
            try: # check if given temperature is a number
                temp = float(group.inputs["temp"].widget.text())
            except ValueError:
                continue # not filled in properly, so skip
            
            index = str(group.inputs["type"].widget.currentText())
            
            # only add to graph if a type is selected
            if len(index) > 0:
                add_mirror(gui, new_graph, index,
                    temp, gui.mirror_consts[index], noise_res)
    
    # Zodiacal emission
    if gui.zodiac_toplot.isChecked():
        # loop through all selected coordinates
        for group in gui.zodiac_collection:
            index = group.inputs["ecrd"].widget.currentIndex()
            # only add to graph if a coordinate is selected
            if index > 0:
                add_zodiac(gui, new_graph,
                    gui.zodiac_files[index - 1], noise_res)
    
    # Cosmic infrared background
    if gui.other_toplot.isChecked() and gui.other_set["cib"].widget.isChecked():
        add_cib(gui, new_graph, noise_res)
    
    # Cosmic microwave background
    if gui.other_toplot.isChecked() and gui.other_set["cmb"].widget.isChecked():
        add_cmb(gui, new_graph, noise_res)
    
    # Signal
    if gui.signal_toplot.isChecked():
        # loop through all aperture/site/source sets
        for group in gui.signal_collection:
            
            try: # check if given aperture is a number
                aperture = float(group.inputs["aperture"].widget.text())
            except ValueError:
                continue # not filled in properly, so skip
            
            site = group.inputs["site"].widget.currentIndex()
            source = group.inputs["source"].widget.currentIndex()
            
            try:
                signal_res = float(gui.signal_res.text())
            except Exception:
                signal_res = config.spec_res
            
            # only add if all fields are filled in
            if site > 0 and source > 0:
                add_signal(gui, new_graph,
                    aperture,
                    gui.atmos_files[site - 1],
                    gui.source_files[source - 1],
                    gui.signal_res.text())
    
    # loop through all sets of inputs
    i = 0
    for group in gui.compos_collection:
        if group.inputs["is_plot"].widget.isChecked() != True:
            continue # not selected for plotting
        if i == len(gui.compos_collection) - 1:
            break # ignore last group
        i += 1
        
        # fetch all valid selected input values (assume "None" by default)
        dataset_label = str(i)
        galactic = aux.name_file("", "")
        mirror_temp = ""
        mirror_type = ""
        zodiac = aux.name_file("", "")
        aperture = ""
        atmos_site = aux.name_file("", "")
        site = aux.name_file("", "")
        source = aux.name_file("", "")
        mirror_constant = -1
        mirror_temp = -1
        aperture = -1
        
        # label for graph
        if len(group.inputs["_label"].widget.text()) > 0:
            dataset_label = group.inputs["_label"].widget.text()
        
        # atmospheric radiance
        atmos_index1 = group.inputs["n_atmos"].widget.currentIndex()
        if atmos_index1 > 0:
            atmos_index2 = gui.atmos_collection[atmos_index1-1].inputs["site"].widget.currentIndex()
            atmos_site = gui.atmos_files[atmos_index2-1]
        
        # galactic emission
        galactic_index1 = group.inputs["n_galactic"].widget.currentIndex()
        if galactic_index1 > 0:
            galactic_index2 = gui.galactic_collection[galactic_index1-1].inputs["gcrd"].widget.currentIndex()
            galactic = gui.galactic_files[galactic_index2-1]
        
        # thermal mirror emission
        mirror_index = group.inputs["n_mirror"].widget.currentIndex()
        if mirror_index > 0:
            type_index = str(gui.mirror_collection[mirror_index-1].inputs["type"].widget.currentText())
            
            mirror_constant = gui.mirror_consts[type_index]
            try:
                mirror_temp = float(gui.mirror_collection[mirror_index-1].inputs["temp"].widget.text())
            except Exception:
                pass
        
        # zodiacal emission
        zodiac_index1 = group.inputs["n_zodiac"].widget.currentIndex()
        if zodiac_index1 > 0:
            zodiac_index2 = gui.zodiac_collection[zodiac_index1-1].inputs["ecrd"].widget.currentIndex()
            zodiac = gui.zodiac_files[zodiac_index2-1]
            
        cib = group.inputs["o_cib"].widget.isChecked()
        cmb = group.inputs["o_cmb"].widget.isChecked()
        
        # signal
        signal_index = group.inputs["signal"].widget.currentIndex()
        if signal_index > 0:
            site_index = gui.signal_collection[signal_index-1].inputs["site"].widget.currentIndex()
            source_index = gui.signal_collection[signal_index-1].inputs["source"].widget.currentIndex()
            
            try:
                aperture = float(gui.signal_collection[signal_index-1].inputs["aperture"].widget.text())
            except Exception:
                pass
            source = gui.source_files[source_index-1]
            if site_index > 0:
                site = gui.atmos_files[site_index-1] # override atmospheric radiance site if provided
        
        if gui.compos_what == 0: # total noise
            add_noise(gui, new_graph, dataset_label, atmos_site,
                    galactic, mirror_temp, mirror_constant, zodiac, cib, cmb)
        
        elif gui.compos_what == 1: # total temperature
            add_temp(gui, new_graph, dataset_label, atmos_site,
                    galactic, mirror_temp, mirror_constant, zodiac, cib, cmb)
        
        elif gui.compos_what == 2: # integration time
            
            try: # check if given signal:noise ratio is a number
                snr = float(group.inputs["snr"].widget.text())
            except ValueError:
                continue # not filled in properly, so skip
            
            try: # check if given spectral resolution is a number
                spec_res = float(group.inputs["specres"].widget.text())
            except ValueError:
                continue # not filled in properly, so skip
            
            add_integ(gui, new_graph, dataset_label, atmos_site, galactic,
                    mirror_temp, mirror_constant, zodiac, cib, cmb, aperture,
                    site, source, snr, spec_res)

    gui.plot.redraw(new_graph)
