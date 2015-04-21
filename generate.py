# generate.py
# generate graph given inputs

import math
import numpy as np

import auxil as aux
import bling
import cal
import config
import const
import dyngui
import graph
import sigtrans
import temp

# return selected units of BLING
def bling_units (gui):
    if gui.bling_units == 0:
        return "W/Hz$^{1/2}$"
    else:
        return "photons/s$\cdot$Hz$^{1/2}$"

# return selected units of flux / intensity
def flux_units (gui):
    if gui.flux_units == 0:
        return "W/sr$\cdot$Hz$\cdot$m$^2$"
    else:
        return "photons/sr$\cdot$Hz$\cdot$m$^2$"

# convert flux to requested units
def flux_convert (gui, flux_list):
    if gui.flux_units == 0: # already in W/sr*Hz*m^2
        return flux_list

    elif gui.flux_units == 1: # convert to photons/sr*Hz*m^2
        return flux_list / (const.h * gui.interp.freq_array)

# build list of graph coordinates from array or list of data
# corresponding to the globally computed list of frequencies
def graph_list (gui, array):

    # build and return list of coordinates
    crdlist = []
    for i, item in enumerate(array):
        crdlist.append(graph.coord_obj(gui.interp.freq_list[i], item))

    return crdlist

# Create data set with proper photon energy type and units
def new_dataset (label, energy_form, dep_type, dep_units, data_hz):

    # build new set of coordinates with proper photon energy form
    crdlist = []
    for hz_crd in data_hz:
        crdlist.append(graph.coord_obj(energy_form.from_hz(hz_crd.x), hz_crd.y))

    return graph.data_set(label, energy_form.type, energy_form.units, dep_type, dep_units, crdlist)

# Add atmospheric radiance to plot
def add_radiance (gui, graph_obj, site_file, spec_res):
    data_name = "Atmos Radiance ("+site_file.name+")"

    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.radiance(gui, site_file.file, spec_res))
        data_set = new_dataset(data_name, gui.energy_form,
                "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(gui, cal.intensity(gui.interp.freq_array,
                                            temp.radiance(gui, site_file.file))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui, temp.radiance(gui, site_file.file))
        data_set = new_dataset("Atmos Radiance ("+site_file.name+")", gui.energy_form,
                "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add atmospheric transmission to plot
def add_trans (gui, graph_obj, site_file):
    trans_list = sigtrans.trans(gui, site_file.file)

    # build and return list of coordinates
    crdlist = []
    for i, trans_val in enumerate(trans_list):
        crdlist.append(graph.coord_obj(gui.interp.freq_list[i], trans_val))

    # build data set and add to graph
    data_set = new_dataset("Atmos Trans ("+site_file.name+")", gui.energy_form,
            "Transmission", "Proportion", crdlist)
    graph_obj.dataset_list.append(data_set)

# Add galactic emission to plot
def add_galactic (gui, graph_obj, galactic_file, spec_res):
    data_name = "Galactic Emission ("+galactic_file.name+")"

    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.generic(gui, galactic_file.file, spec_res))
        data_set = new_dataset(data_name,
                gui.energy_form, "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(gui, cal.intensity(gui.interp.freq_array,
                              temp.generic(gui, galactic_file.file))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui, temp.generic(gui, galactic_file.file))
        data_set = new_dataset(data_name,
                gui.energy_form, "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add thermal mirror emission to plot
def add_mirror (gui, graph_obj, metal_name, mirror_temp, constant, spec_res):
    data_name = "Thermal Mirror ("+metal_name+", "+str(mirror_temp)+" K)"

    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.mirror(gui,
                mirror_temp, constant, spec_res))
        data_set = new_dataset(data_name,
                gui.energy_form, "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(gui, cal.intensity(gui.interp.freq_array,
                              temp.mirror(gui, mirror_temp, constant))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui, temp.mirror(gui, mirror_temp, constant))
        data_set = new_dataset(data_name,
                gui.energy_form, "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add zodiacal emission to plot
def add_zodiac (gui, graph_obj, zodiac_file, spec_res):
    data_name = "Zodiacal Emission ("+zodiac_file.name+")"

    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.generic(gui, zodiac_file.file, spec_res))
        data_set = new_dataset(data_name,
                gui.energy_form, "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(gui, cal.intensity(gui.interp.freq_array,
                              temp.generic(gui, zodiac_file.file))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui, temp.generic(gui, zodiac_file.file))
        data_set = new_dataset(data_name,
                gui.energy_form, "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add cosmic infrared background to plot
def add_cib (gui, graph_obj, spec_res):
    data_name = "Cosmic Infrared Bkgd"

    # TODO: convert to equation fit
    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.generic(gui,
                "data/Backgrounds/CIB/cib.xlsx", spec_res))
        data_set = new_dataset(data_name, gui.energy_form,
                               "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(cal.intensity(gui.interp.freq_array,
                         temp.generic(gui, "data/Backgrounds/CIB/cib.xlsx"))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui,
            temp.generic(gui, "data/Backgrounds/CIB/cib.xlsx"))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add cosmic microwave background to plot
def add_cmb (gui, graph_obj, spec_res):
    data_name = "Cosmic Microwave Bkgd"

    if gui.noise_what == 0: # BLING
        bling_list = graph_list(gui, bling.cmb(gui, spec_res))
        data_set = new_dataset(data_name, gui.energy_form,
                               "BLING", bling_units(gui), bling_list)

    elif gui.noise_what == 1: # flux
        flux_list = graph_list(gui,
            flux_convert(gui,
                         cal.intensity(gui.interp.freq_array, temp.cmb(gui))))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Flux", flux_units(gui), flux_list)

    else: # temperature
        temp_list = graph_list(gui, temp.cmb(gui))
        data_set = new_dataset(data_name, gui.energy_form,
                               "Temperature", "K", temp_list)

    graph_obj.dataset_list.append(data_set)

# Add signal to plot
def add_signal (gui, graph_obj, aperture, site_file, source_file, spec_res):
    sig_list = sigtrans.signal(gui, aperture, site_file.file, source_file.file, spec_res)

    # build and return list of coordinates
    crdlist = []
    for i, signal_val in enumerate(sig_list):
        crdlist.append(graph.coord_obj(gui.interp.freq_list[i], signal_val))

    # build data set and add to graph
    data_set = new_dataset(
        "Signal ("+str(aperture)+" m, "+site_file.name+", "+source_file.name+")",
         gui.energy_form, "Signal", "W", crdlist)
    graph_obj.dataset_list.append(data_set)

## Composite calculations
# (note: some parameters passed may be "None" -- these are ignored if possible)

# Add total BLING to plot
def add_bling (gui, graph_obj, label, site_file, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb, spec_res):

    blingsq_tot = bling.noise_total(gui, site_file.file, galactic_file.file,
        mirror_temp, mirror_constant, zodiac_file.file, cib, cmb, spec_res)
    data_set = new_dataset("Total Noise ("+label+")", gui.energy_form,
                           "BLING", bling_units(gui),
                           graph_list(gui, blingsq_tot))
    graph_obj.dataset_list.append(data_set)

# Add total flux to plot
def add_flux (gui, graph_obj, label, atmos_site, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb):

    temp_tot = temp.total(gui, atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb)
    flux_tot = flux_convert(gui, cal.intensity(gui.interp.freq_array, temp_tot))
    data_set = new_dataset("Total Flux ("+label+")", gui.energy_form,
                           "Flux", flux_units(gui), graph_list(gui, flux_tot))
    graph_obj.dataset_list.append(data_set)

# Add total temp to plot
def add_temp (gui, graph_obj, label, atmos_site, galactic_file, mirror_temp,
        mirror_constant, zodiac_file, cib, cmb):

    temp_tot = temp.total(gui, atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb)
    data_set = new_dataset("Total Temp ("+label+")", gui.energy_form,
                           "Temperature", "K", graph_list(gui, temp_tot))
    graph_obj.dataset_list.append(data_set)

# Add integration time to plot
def add_integ (gui, graph_obj, label, atmos_site, galactic_file, mirror_temp, mirror_constant,
        zodiac_file, cib, cmb, aperture, site_file, source_file, snr, spec_res):

    # compute noise and signal and, with signal:noise ratio, integration time
    blingsq_tot = bling.noise_total(gui, atmos_site.file, galactic_file.file, mirror_temp,
        mirror_constant, zodiac_file.file, cib, cmb, spec_res)
    sig_list = sigtrans.signal(gui, aperture, site_file.file, source_file.file, spec_res)
    integ_time = cal.IT(blingsq_tot, snr, sig_list) # array of integration times

    # build and return list of coordinates
    crdlist = []
    for i, integ_val in enumerate(integ_time):
        crdlist.append(graph.coord_obj(gui.interp.freq_list[i], integ_val))

    # build data set and add to graph
    data_set = new_dataset("Integration Time ("+label+")", gui.energy_form, "Time", "s", crdlist)
    graph_obj.dataset_list.append(data_set)

# generate a graph with inputs
def process (gui):

    new_graph = graph.graph_obj(gui.config_sets[0]["name"].widget.text(), [])

    gui.energy_form = gui.energy_list[gui.config_sets[1]["e_units"].widget.currentIndex()]
    gui.bling_units = gui.config_sets[2]["b_units"].widget.currentIndex()
    gui.flux_units = gui.config_sets[2]["f_units"].widget.currentIndex()
    gui.compos_what = gui.compos_whatbox.currentIndex()
    gui.noise_what = gui.noise_whatbox.currentIndex()

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
                signal_res = float(config.spec_res)

            # only add if source is filled in (assume site=space by default)
            if source > 0:
                add_signal(gui, new_graph,
                    aperture,
                    site > 0 and gui.atmos_files[site - 1]
                              or aux.name_file("", False),
                    gui.source_files[source - 1],
                    signal_res)

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

        try: # check if given spectral resolution is a number
            spec_res = float(group.inputs["specres"].widget.text())
        except ValueError:
            continue # not filled in properly, so skip

        if gui.compos_what == 0: # total BLING
            add_bling(gui, new_graph, dataset_label, atmos_site, galactic,
                      mirror_temp, mirror_constant, zodiac, cib, cmb, spec_res)

        elif gui.compos_what == 1: # total noise flux
            add_flux(gui, new_graph, dataset_label, atmos_site, galactic,
                     mirror_temp, mirror_constant, zodiac, cib, cmb)

        elif gui.compos_what == 2: # total temperature
            add_temp(gui, new_graph, dataset_label, atmos_site, galactic,
                     mirror_temp, mirror_constant, zodiac, cib, cmb)

        elif gui.compos_what == 3: # integration time

            try: # check if given signal:noise ratio is a number
                snr = float(group.inputs["snr"].widget.text())
            except ValueError:
                continue # not filled in properly, so skip

            add_integ(gui, new_graph, dataset_label, atmos_site, galactic,
                      mirror_temp, mirror_constant, zodiac, cib, cmb, aperture,
                      site, source, snr, spec_res)

    return new_graph
