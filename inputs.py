# inputs.py
# groups of widgets that are the inputs in the calculations

from PyQt4 import QtCore, QtGui

import auxil as aux
import config
import const
import dyngui

# Project Configuration
def pconfig(gui):

    inputs1 = {} # identifying information

    inputs1["name"] = dyngui.input_obj("Name", QtGui.QLineEdit())

    # dynamically change the title on the graph
    def name_changed(text):

        # update title of graph
        gui.plot.set_title(text)

        # mark that project has been edited since last save
        gui.changed = True

    QtCore.QObject.connect(inputs1["name"].widget,
            QtCore.SIGNAL("textChanged(QString)"), name_changed)

    inputs2 = {} # photon energy units and range

    energy = QtGui.QComboBox()
    for option in gui.energy_list:
        energy.addItem(option.type + " (" + option.units + ")")
    inputs2["e_units"] = dyngui.input_obj("Photon Energy", energy)

    def e_units_changed(new_index): # handle changed in selected units of photon energy

        # do unit conversions for min and max energies
        energy_min = gui.energy_list[new_index].from_hz(gui.interp.freq_range.min)
        energy_max = gui.energy_list[new_index].from_hz(gui.interp.freq_range.max)

        # assign to "min" and "max" text fields by numerical value
        #  (ie. smaller wavelengths correspond to higher energy, so need to reverse)
        if energy_min < energy_max: # order already correct
            inputs2["energy1"].widget.setText(str(energy_min))
            inputs2["energy2"].widget.setText(str(energy_max))
        else: # order reversed
            inputs2["energy2"].widget.setText(str(energy_min))
            inputs2["energy1"].widget.setText(str(energy_max))

        # mark that project has been edited since last save
        gui.changed = True

    QtCore.QObject.connect(inputs2["e_units"].widget,
            QtCore.SIGNAL("currentIndexChanged(int)"), e_units_changed)

    # minimum and maximum energies in units defined above
    inputs2["energy1"] = dyngui.input_obj("Minimum", QtGui.QLineEdit())
    inputs2["energy2"] = dyngui.input_obj("Maximum", QtGui.QLineEdit())

    # set presently active range of energies as default text
    e_units_changed(inputs2["e_units"].widget.currentIndex())

    # convert currently entered text to frequency range
    def energy_changed(text):

        try: # ensure both fields are filled with floating point numbers

            # currently selected unit of photon energy
            energy_form = gui.energy_list[inputs2["e_units"].widget.currentIndex()]

            freq1 = energy_form.to_hz(float(inputs2["energy1"].widget.text()))
            freq2 = energy_form.to_hz(float(inputs2["energy2"].widget.text()))

            if freq1 < freq2:
                freq_range = aux.interval(freq1, freq2)
            else:
                freq_range = aux.interval(freq2, freq1)

            # set interpolation range
            if energy_form.is_freq:
                gui.interp.set_freq_hz(freq_range)
            else:
                gui.interp.set_wl_m(aux.interval(const.c / freq_range.max,
                    const.c / freq_range.min))

        except Exception:
            pass # assume fields are incomplete, so ignore now and try again later

        # mark that project has been edited since last save
        gui.changed = True

    QtCore.QObject.connect(inputs2["energy1"].widget,
            QtCore.SIGNAL("textChanged(QString)"), energy_changed)
    QtCore.QObject.connect(inputs2["energy2"].widget,
            QtCore.SIGNAL("textChanged(QString)"), energy_changed)

    inputs3 = {} # units

    bling = QtGui.QComboBox() # units of bling
    bling.addItems(["W/Hz^1/2", "photons/s*Hz^1/2"])
    inputs3["b_units"] = dyngui.input_obj("Units of BLING", bling)
    conn_changed(gui, bling, "currentIndexChanged(int)")

    flux = QtGui.QComboBox() # units of flux
    flux.addItems(["W/sr*Hz*m^2", "photons/sr*Hz*m^2"])
    inputs3["f_units"] = dyngui.input_obj("Units of Flux", flux)
    conn_changed(gui, flux, "currentIndexChanged(int)")

    return inputs1, inputs2, inputs3

# Atmospheric Radiance & Transmission
def atmos(gui, fields = {"site" : 0}):

    inputs = {}
    site = QtGui.QComboBox()
    site.addItem("")
    add_list(site, gui.atmos_files)
    site.setCurrentIndex(int(fields["site"]))

    conn_update(gui, site, "currentIndexChanged(int)")
    inputs["site"] = dyngui.input_obj("Site", site)

    return inputs

# Galactic Emission
def galactic(gui, fields = {"gcrd" : 0}):

    inputs = {}

    coord = QtGui.QComboBox()
    coord.addItem("")
    add_list(coord, gui.galactic_files)
    coord.setCurrentIndex(int(fields["gcrd"]))

    conn_update(gui, coord, "currentIndexChanged(int)")
    inputs["gcrd"] = dyngui.input_obj("Galactic Coord", coord)

    return inputs

# Thermal Mirror Emission
def mirror(gui, fields = {"temp" : "", "type" : 0}):

    inputs = {}

    inputs["temp"] = dyngui.input_obj("Temperature (K)", QtGui.QLineEdit())
    inputs["temp"].widget.setText(str(fields["temp"]))
    conn_update(gui, inputs["temp"].widget, "textChanged(QString)")

    mirror_type = QtGui.QComboBox()
    mirror_type.addItem("")
    for material, const in gui.mirror_consts.items():
        mirror_type.addItem(material)
    mirror_type.setCurrentIndex(int(fields["type"]))

    conn_update(gui, mirror_type, "currentIndexChanged(int)")
    inputs["type"] = dyngui.input_obj("Mirror Type", mirror_type)

    return inputs

# Zodiacal Emission
def zodiac(gui, fields = {"ecrd" : 0}):

    inputs = {}

    coord = QtGui.QComboBox()
    coord.addItem("")
    add_list(coord, gui.zodiac_files)
    coord.setCurrentIndex(int(fields["ecrd"]))

    conn_update(gui, coord, "currentIndexChanged(int)")
    inputs["ecrd"] = dyngui.input_obj("Ecliptic Coord", coord)

    return inputs

# Other Noise
def other(gui):

    inputs = {}

    cib = QtGui.QCheckBox("Cosmic Infrared Background")
    cib.setCheckState(QtCore.Qt.Checked)
    cmb = QtGui.QCheckBox("Cosmic Microwave Background")
    cmb.setCheckState(QtCore.Qt.Checked)

    inputs["cib"] = dyngui.input_obj("", cib)
    inputs["cmb"] = dyngui.input_obj("", cmb)

    return inputs

# Signal
def signal(gui, fields = {"aperture" : "", "site" : 0, "source" : 0}):

    inputs = {}

    inputs["aperture"] = dyngui.input_obj("Aperture (m)", QtGui.QLineEdit())
    inputs["aperture"].widget.setText(str(fields["aperture"]))
    conn_update(gui, inputs["aperture"].widget, "textChanged(QString)")

    site = QtGui.QComboBox()
    site.addItem("")
    add_list(site, gui.atmos_files)
    site.setCurrentIndex(int(fields["site"]))

    conn_update(gui, site, "currentIndexChanged(int)")
    inputs["site"] = dyngui.input_obj("Site", site)
    inputs["site"].widget.setToolTip("Leave empty for 100% transmission")
    inputs["site"].widget.setMouseTracking(True)

    source = QtGui.QComboBox()
    source.addItem("")
    add_list(source, gui.source_files)
    source.setCurrentIndex(int(fields["source"]))

    conn_update(gui, source, "currentIndexChanged(int)")
    inputs["source"] = dyngui.input_obj("Source", source)

    return inputs

# Composite Data Calculations
def compos(gui, fields = {"_label" : "", "is_plot" : False,
        "n_atmos" : 0, "n_galactic" : 0, "n_mirror" : 0, "n_zodiac" : 0,
        "o_cib" : False, "o_cmb" : False,
        "signal" : 0, "snr" : "", "specres" : ""}):

    inputs = {}

    # label for composite graph
    label = QtGui.QLineEdit()
    label.setText(str(fields["_label"]))
    conn_update(gui, label, "textChanged(QString)")

    # initialize drop down boxes
    atmos = QtGui.QComboBox()
    dyngui.update_list(atmos, gui.atmos_collection)
    atmos.setCurrentIndex(int(fields["n_atmos"]))
    conn_update(gui, atmos, "currentIndexChanged(int)")

    galactic = QtGui.QComboBox()
    dyngui.update_list(galactic, gui.galactic_collection)
    galactic.setCurrentIndex(int(fields["n_galactic"]))
    conn_update(gui, galactic, "currentIndexChanged(int)")

    mirror = QtGui.QComboBox()
    dyngui.update_list(mirror, gui.mirror_collection)
    mirror.setCurrentIndex(int(fields["n_mirror"]))
    conn_update(gui, mirror, "currentIndexChanged(int)")

    zodiac = QtGui.QComboBox()
    dyngui.update_list(zodiac, gui.zodiac_collection)
    zodiac.setCurrentIndex(int(fields["n_zodiac"]))
    conn_update(gui, zodiac, "currentIndexChanged(int)")

    signal = QtGui.QComboBox()
    dyngui.update_list(signal, gui.signal_collection)
    signal.setCurrentIndex(int(fields["signal"]))
    conn_update(gui, signal, "currentIndexChanged(int)")

    # initialize checkboxes
    cib = QtGui.QCheckBox("Cosmic Infrared Background")
    cib.setCheckState(fields["o_cib"] == "True" and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
    conn_update(gui, cib, "stateChanged(int)")

    cmb = QtGui.QCheckBox("Cosmic Microwave Background")
    cmb.setCheckState(fields["o_cmb"] == "True" and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
    conn_update(gui, cmb, "stateChanged(int)")

    isplot = QtGui.QCheckBox("Plot this data")
    isplot.setCheckState(fields["is_plot"] == "True" and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
    conn_update(gui, isplot, "stateChanged(int)")

    # signal:noise ratio
    snr = QtGui.QLineEdit()
    snr.setText(str(fields["snr"]))
    conn_update(gui, snr, "textChanged(QString)")

    # spectral resolution
    specres = QtGui.QLineEdit()
    specres.setText(str(fields["specres"]))
    conn_update(gui, specres, "textChanged(QString)")

    inputs["_label"] = dyngui.input_obj("Label", label)
    inputs["is_plot"] = dyngui.input_obj("", isplot)
    inputs["n_atmos"] = dyngui.input_obj("Atmosphere", atmos)
    inputs["n_galactic"] = dyngui.input_obj("Galactic", galactic)
    inputs["n_mirror"] = dyngui.input_obj("Mirror", mirror)
    inputs["n_zodiac"] = dyngui.input_obj("Zodiacal", zodiac)
    inputs["o_cib"] = dyngui.input_obj("", cib)
    inputs["o_cmb"] = dyngui.input_obj("", cmb)
    inputs["signal"] = dyngui.input_obj("Signal", signal)
    inputs["snr"] = dyngui.input_obj("Signal:Noise", snr)
    inputs["specres"] = dyngui.input_obj("Resolution", specres)

    # clear all inputs in this set
    def clear():
        inputs["_label"].widget.setText("")
        inputs["is_plot"].widget.setCheckState(QtCore.Qt.Unchecked)
        inputs["n_atmos"].widget.setCurrentIndex(0)
        inputs["n_galactic"].widget.setCurrentIndex(0)
        inputs["n_mirror"].widget.setCurrentIndex(0)
        inputs["n_zodiac"].widget.setCurrentIndex(0)
        inputs["o_cib"].widget.setCheckState(QtCore.Qt.Unchecked)
        inputs["o_cmb"].widget.setCheckState(QtCore.Qt.Unchecked)
        inputs["signal"].widget.setCurrentIndex(0)
        inputs["snr"].widget.setText("")
        inputs["specres"].widget.setText("")
        update_all(gui)

    inputs["z_clear"] = dyngui.input_obj("", QtGui.QPushButton("Clear Fields"))
    QtCore.QObject.connect(inputs["z_clear"].widget, QtCore.SIGNAL("clicked()"), clear)

    # select first item in each input box
    def default():
        if len(inputs["n_atmos"].widget) > 1:
            inputs["n_atmos"].widget.setCurrentIndex(1)
        if len(inputs["n_galactic"].widget) > 1:
            inputs["n_galactic"].widget.setCurrentIndex(1)
        if len(inputs["n_mirror"].widget) > 1:
            inputs["n_mirror"].widget.setCurrentIndex(1)
        if len(inputs["n_zodiac"].widget) > 1:
            inputs["n_zodiac"].widget.setCurrentIndex(1)

        inputs["o_cib"].widget.setCheckState(config.use_cib and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
        inputs["o_cmb"].widget.setCheckState(config.use_cmb and QtCore.Qt.Checked or QtCore.Qt.Unchecked)

        if len(inputs["signal"].widget) > 1:
            inputs["signal"].widget.setCurrentIndex(1)
        inputs["snr"].widget.setText(config.snr) # default signal:noise
        inputs["specres"].widget.setText(config.spec_res) # default spectral resolution
        update_all(gui)

    inputs["z_default"] = dyngui.input_obj("", QtGui.QPushButton("Use Default"))
    QtCore.QObject.connect(inputs["z_default"].widget, QtCore.SIGNAL("clicked()"), default)

    return inputs

# connect widgets to update function
def conn_update(gui, widget, sig):
    QtCore.QObject.connect(widget, QtCore.SIGNAL(sig), aux.func_arg(update_all, gui))

# connect widgets to changed function
def conn_changed(gui, widget, sig):
    QtCore.QObject.connect(widget, QtCore.SIGNAL(sig), aux.func_arg(changed, gui))

# add file list to drop down list
def add_list(drop_down, file_list):
    for item in file_list:
        drop_down.addItem(item.name)

# mark that project has changed
def changed(gui):
    gui.changed = True

# Propogate changes by updating all dynamic elements
def update_all(gui):

    # update all collections of widget groups
    dyngui.update_collection(gui.atmos_collection, gui.atmos_list, aux.func_arg(atmos, gui))
    dyngui.update_collection(gui.galactic_collection, gui.galactic_list, aux.func_arg(galactic, gui))
    dyngui.update_collection(gui.mirror_collection, gui.mirror_list, aux.func_arg(mirror, gui))
    dyngui.update_collection(gui.zodiac_collection, gui.zodiac_list, aux.func_arg(zodiac, gui))
    dyngui.update_collection(gui.signal_collection, gui.signal_list, aux.func_arg(signal, gui))
    dyngui.update_tabcollect(gui.compos_collection, gui.compos_tabs, aux.func_arg(compos, gui))

    # update composite tab
    for group in gui.compos_collection:
        dyngui.update_list(group.inputs["n_atmos"].widget, gui.atmos_collection)
        dyngui.update_list(group.inputs["n_galactic"].widget, gui.galactic_collection)
        dyngui.update_list(group.inputs["n_mirror"].widget, gui.mirror_collection)
        dyngui.update_list(group.inputs["n_zodiac"].widget, gui.zodiac_collection)
        dyngui.update_list(group.inputs["signal"].widget, gui.signal_collection)

    # mark that project has been edited since last save
    gui.changed = True
