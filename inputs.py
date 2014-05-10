# inputs.py
# groups of widgets that are the inputs in the calculations

from PyQt4 import QtCore, QtGui
import dyngui

# Atmospheric Radiance & Transmission
def atmos(gui):
    
    inputs = {}
    site = QtGui.QComboBox()
    site.addItem("")
    add_list(site, gui.atmos_files)
    conn_update(gui, site, "currentIndexChanged(int)")
    inputs["site"] = dyngui.input_obj("Site", site)
    
    return inputs

# Galactic Emission
def galactic(gui):
    
    inputs = {}
    
    coord = QtGui.QComboBox()
    coord.addItem("")
    add_list(coord, gui.galactic_files)
    conn_update(gui, coord, "currentIndexChanged(int)")
    inputs["gcrd"] = dyngui.input_obj("Galactic Coord", coord)
    
    return inputs

# Thermal Mirror Emission
def mirror(gui):
    
    inputs = {}
    
    inputs["temp"] = dyngui.input_obj("Temperature (K)", QtGui.QLineEdit())
    conn_update(gui, inputs["temp"].widget, "textChanged(QString)")
    
    mirror_type = QtGui.QComboBox()
    mirror_type.addItem("")
    add_list(mirror_type, gui.mirror_files)
    conn_update(gui, mirror_type, "currentIndexChanged(int)")
    inputs["type"] = dyngui.input_obj("Mirror Type", mirror_type)
    
    return inputs
    
# Zodiacal Emission
def zodiac(gui):
    
    inputs = {}
    
    coord = QtGui.QComboBox()
    coord.addItem("")
    add_list(coord, gui.zodiac_files)
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
def signal(gui):
    
    inputs = {}
    
    inputs["aper"] = dyngui.input_obj("Aperture (m)", QtGui.QLineEdit())
    conn_update(gui, inputs["aper"].widget, "textChanged(QString)")
    
    site = QtGui.QComboBox()
    site.addItem("")
    add_list(site, gui.atmos_files)
    conn_update(gui, site, "currentIndexChanged(int)")
    inputs["site"] = dyngui.input_obj("Site", site)
    
    source = QtGui.QComboBox()
    source.addItem("")
    add_list(source, gui.source_files)
    conn_update(gui, source, "currentIndexChanged(int)")
    inputs["source"] = dyngui.input_obj("Source", source)
    
    return inputs
    
# Composite Data Calculations
def compos(gui):
    
    inputs = {}
    
    # initialize drop down boxes
    atmos = QtGui.QComboBox()
    dyngui.update_list(atmos, gui.atmos_collection)
    conn_update(gui, atmos, "currentIndexChanged(int)")
    
    galactic = QtGui.QComboBox()
    dyngui.update_list(galactic, gui.galactic_collection)
    conn_update(gui, galactic, "currentIndexChanged(int)")
    
    mirror = QtGui.QComboBox()
    dyngui.update_list(mirror, gui.mirror_collection)
    conn_update(gui, mirror, "currentIndexChanged(int)")
    
    zodiac = QtGui.QComboBox()
    dyngui.update_list(zodiac, gui.zodiac_collection)
    conn_update(gui, zodiac, "currentIndexChanged(int)")
    
    signal = QtGui.QComboBox()
    dyngui.update_list(signal, gui.signal_collection)
    conn_update(gui, signal, "currentIndexChanged(int)")
    
    # initialize checkboxes
    cib = QtGui.QCheckBox("Cosmic Infrared Background")
    cib.setCheckState(QtCore.Qt.Checked)
    cmb = QtGui.QCheckBox("Cosmic Microwave Background")
    cmb.setCheckState(QtCore.Qt.Checked)
    
    inputs["n_atmos"] = dyngui.input_obj("Atmosphere", atmos)
    inputs["n_galactic"] = dyngui.input_obj("Galactic", galactic)
    inputs["n_mirror"] = dyngui.input_obj("Mirror", mirror)
    inputs["n_zodiac"] = dyngui.input_obj("Zodiacal", zodiac)
    inputs["o_cib"] = dyngui.input_obj("", cib)
    inputs["o_cmb"] = dyngui.input_obj("", cmb)
    inputs["signal"] = dyngui.input_obj("Signal", signal)
    inputs["snr"] = dyngui.input_obj("Signal:Noise", QtGui.QLineEdit())
    
    # clear all inputs in this set
    def clear():
        inputs["n_atmos"].widget.setCurrentIndex(0)
        inputs["n_galactic"].widget.setCurrentIndex(0)
        inputs["n_mirror"].widget.setCurrentIndex(0)
        inputs["n_zodiac"].widget.setCurrentIndex(0)
        inputs["signal"].widget.setCurrentIndex(0)
        inputs["snr"].widget.setText("")
        update_all(gui)
    
    inputs["z_clear"] = dyngui.input_obj("", QtGui.QPushButton("Clear Fields"))
    QtCore.QObject.connect(inputs["z_clear"].widget, QtCore.SIGNAL("clicked()"), clear)
    
    # select first item in each input box
    def default():
        inputs["n_atmos"].widget.setCurrentIndex(1)
        inputs["n_galactic"].widget.setCurrentIndex(1)
        inputs["n_mirror"].widget.setCurrentIndex(1)
        inputs["n_zodiac"].widget.setCurrentIndex(1)
        
        inputs["o_cib"].widget.setCheckState(QtCore.Qt.Checked)
        inputs["o_cmb"].widget.setCheckState(QtCore.Qt.Checked)
        
        inputs["signal"].widget.setCurrentIndex(1)
        inputs["snr"].widget.setText("3") # default signal:noise = 3
        update_all(gui)
    
    inputs["z_default"] = dyngui.input_obj("", QtGui.QPushButton("Use Default"))
    QtCore.QObject.connect(inputs["z_default"].widget, QtCore.SIGNAL("clicked()"), default)
    
    return inputs

# return a function (fx) equivalent to another (func) being passed an argument (arg)
def func_arg(func, arg):
    
    def fx():
        return func(arg)
    
    return fx

# connect widgets to update function
def conn_update(gui, widget, sig):
    QtCore.QObject.connect(widget, QtCore.SIGNAL(sig), func_arg(update_all, gui))

# add file list to drop down list
def add_list(drop_down, file_list):
    for item in file_list:
        drop_down.addItem(item.name)

# Propogate changes by updating all dynamic elements
def update_all(gui):
    
    # update all collections of widget groups
    dyngui.update_collection(gui.atmos_collection, gui.atmos_list, func_arg(atmos, gui))
    dyngui.update_collection(gui.galactic_collection, gui.galactic_list, func_arg(galactic, gui))
    dyngui.update_collection(gui.mirror_collection, gui.mirror_list, func_arg(mirror, gui))
    dyngui.update_collection(gui.zodiac_collection, gui.zodiac_list, func_arg(zodiac, gui))
    dyngui.update_collection(gui.signal_collection, gui.signal_list, func_arg(signal, gui))
    dyngui.update_collection(gui.compos_collection, gui.compos_clayout, func_arg(compos, gui))
    
    # update composite tab
    for group in gui.compos_collection:
        dyngui.update_list(group.inputs["n_atmos"].widget, gui.atmos_collection)
        dyngui.update_list(group.inputs["n_galactic"].widget, gui.galactic_collection)
        dyngui.update_list(group.inputs["n_mirror"].widget, gui.mirror_collection)
        dyngui.update_list(group.inputs["n_zodiac"].widget, gui.zodiac_collection)
        dyngui.update_list(group.inputs["signal"].widget, gui.signal_collection)