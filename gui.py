# gui.py
# graphical interface

import collections
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QTAgg as NavigationToolbar

import aux
import dyngui
import generate
import graph
from graph import *
import inputs

class gui(QtGui.QWidget):
    
    def __init__(self, energy_list, sites, source, galactic, mirror, zodiac):
        super(gui, self).__init__()
        
        self.energy_list = energy_list # ways of measuring photon energy
        self.freq_range = aux.interval(1e11, 1e13) # frequency range for plot (Hz)
        
        self.atmos_files = sites # list of observer sites
        self.source_files = source # list of source galaxies
        self.galactic_files = galactic # list of galactic emission files
        self.mirror_consts = mirror # dictionary of constants for mirror types (metals)
        self.zodiac_files = zodiac # list of ecliptic emission files
        
        self.changed = False # no edits made so far
        self.init_UI()
    
    # center the window
    def center(self):
        rect = self.frameGeometry()
        center_pos = QtGui.QDesktopWidget().availableGeometry().center()
        rect.moveCenter(center_pos)
        self.move(rect.topLeft())

    # draw the interface
    def init_UI(self):
        
        # setup the window
        self.resize(1000, 580)
        self.center()
        self.showMaximized()
        self.setWindowTitle("Atmospheric Modeling")
        
        ###
        ### Left Side (input settings)
        ###
        
        left = QtGui.QVBoxLayout()
        
        left_tabs = QtGui.QTabWidget()
        left_tabs.setTabPosition(QtGui.QTabWidget.North)
        left_tabs.setFixedWidth(400)
        left.addWidget(left_tabs, 0, QtCore.Qt.AlignLeft)
        
        ## -- SETTINGS -- ##
        
        config_panel = QtGui.QWidget()
        left_tabs.addTab(config_panel, "Settings")
        
        config_layout = QtGui.QVBoxLayout()
        config_panel.setLayout(config_layout)
        
        config_layout.addWidget(QtGui.QLabel("<h3>Project Configuration</h3>"), 0, QtCore.Qt.AlignHCenter)
        
        # container holding input controls
        config_area = QtGui.QScrollArea()
        config_area.setFrameShape(QtGui.QFrame.NoFrame) # don't show the border
        config_layout.addWidget(config_area)
        
        # list of groups of input controls
        config_controls = QtGui.QFormLayout()
        config_area.setLayout(config_controls)
        
        self.config_sets = inputs.config(self)
        for single_set in self.config_sets:
            dyngui.new_group(config_controls, single_set)
        
        ## -- NOISE -- ##
        
        noise_panel = QtGui.QWidget()
        left_tabs.addTab(noise_panel, "Noise")
        noise_layout = QtGui.QVBoxLayout()
        noise_panel.setLayout(noise_layout)
        
        # tabbed control with different types of noise
        
        noise_tabs = QtGui.QTabWidget()
        noise_tabs.setTabPosition(QtGui.QTabWidget.West)
        noise_layout.addWidget(noise_tabs)
        
        # Atmospheric Radiance / Transmission
        
        self.atmos_toplot = [QtGui.QCheckBox("Plot Radiance"), QtGui.QCheckBox("Plot Transmission")]
        ignored_value, self.atmos_list =  dyngui.add_tab(
            noise_tabs, "Atmospheric", "Earth's Atmosphere", self.atmos_toplot)
        self.atmos_collection = []
        
        atmos_set0 = inputs.atmos(self)
        self.atmos_collection.append(dyngui.collect_obj(atmos_set0,
                dyngui.new_group(self.atmos_list, atmos_set0)))
        
        # Galactic Emission
        
        self.galactic_toplot, self.galactic_list = dyngui.add_tab(noise_tabs, "Galactic", "Galactic Emission")
        self.galactic_collection = []
        
        galactic_set0 = inputs.galactic(self)
        self.galactic_collection.append(dyngui.collect_obj(galactic_set0,
                dyngui.new_group(self.galactic_list, galactic_set0)))
        
        # Thermal Mirror Emission
        
        self.mirror_toplot, self.mirror_list = dyngui.add_tab(noise_tabs, "Mirror", "Thermal Mirror Emission")
        self.mirror_collection = []
        self.mirror_groups = []
        
        mirror_set0 = inputs.mirror(self)
        self.mirror_collection.append(dyngui.collect_obj(mirror_set0,
                dyngui.new_group(self.mirror_list, mirror_set0)))
        
        # Zodiacal Emission
        
        self.zodiac_toplot, self.zodiac_list = dyngui.add_tab(noise_tabs, "Zodiacal", "Zodiacal Emission")
        self.zodiac_collection = []
        self.zodiac_groups = []
        
        zodiac_set0 = inputs.zodiac(self)
        self.zodiac_collection.append(dyngui.collect_obj(zodiac_set0,
                dyngui.new_group(self.zodiac_list, zodiac_set0)))
        
        # Other Noise
        
        self.other_toplot, other_list = dyngui.add_tab(noise_tabs, "Other", "Other Noise")
        
        self.other_set = inputs.other(self)
        dyngui.new_group(other_list, self.other_set)
        
        ## -- SIGNAL -- ##
        
        self.signal_toplot, self.signal_list = dyngui.add_tab(left_tabs, "Signal", "Signal")
        self.signal_collection = []
        self.signal_groups = []
        
        signal_set0 = inputs.signal(self)
        self.signal_collection.append(dyngui.collect_obj(signal_set0,
                dyngui.new_group(self.signal_list, signal_set0)))
        
        ## -- COMPOSITE -- ##
        
        compos_panel = QtGui.QWidget()
        left_tabs.addTab(compos_panel, "Composite")
        
        compos_layout = QtGui.QVBoxLayout()
        compos_panel.setLayout(compos_layout)
        
        # tabbed control with different types of noise
        
        self.compos_tabs = QtGui.QTabWidget()
        self.compos_tabs.setTabPosition(QtGui.QTabWidget.West)
        compos_layout.addWidget(self.compos_tabs)
        
        # collection of widgets
        self.compos_collection = []
        
        compos_set0 = inputs.compos(self)
        
        self.compos_collection.append(dyngui.collect_obj(compos_set0,
            dyngui.new_group_tab(self.compos_tabs, compos_set0, "New")))
        
        # what to plot
        compos_what = QtGui.QWidget()
        compos_layout.addWidget(compos_what, 0, QtCore.Qt.AlignHCenter)
        compos_whatlo = QtGui.QFormLayout()
        compos_what.setLayout(compos_whatlo)
        
        self.compos_whatbox = QtGui.QComboBox()
        self.compos_whatbox.addItem("None")
        self.compos_whatbox.addItem("Total Noise")
        self.compos_whatbox.addItem("Total Temperature")
        self.compos_whatbox.addItem("Integration Time")
        
        compos_whatlo.addRow("Plot:", self.compos_whatbox)
        
        ###
        ### Right Side (input settings)
        ###
        
        right = QtGui.QVBoxLayout()
        
        ## menu bar
        menu_layout = QtGui.QVBoxLayout()
        right.addLayout(menu_layout)
        
        menu = QtGui.QMenuBar()
        menu_layout.addWidget(menu)
        
        # open project file
        def open_func():
            None
        
        openprj = QtGui.QAction("&Open", self)
        openprj.setStatusTip("Open project file")
        openprj.setShortcut("Ctrl+O")
        openprj.triggered.connect(open_func)
        menu.addAction(openprj)
        
        # save project file
        def save_func():
            None
        
        saveprj = QtGui.QAction("&Save", self)
        saveprj.setStatusTip("Save project file")
        saveprj.setShortcut("Ctrl+S")
        saveprj.triggered.connect(save_func)
        menu.addAction(saveprj)
        
        # save project file with different name
        def saveas_func():
            None
        
        saveas = QtGui.QAction("Save As", self)
        saveas.setStatusTip("Save project file with different name")
        saveas.triggered.connect(saveas_func)
        menu.addAction(saveas)
        
        # export data
        def export_func():
            None
        
        export = QtGui.QAction("Export", self)
        export.setStatusTip("Export data in graph")
        export.triggered.connect(export_func)
        menu.addAction(export)
        
        ## Graph and toolbar
        graph_layout = QtGui.QVBoxLayout()
        right.addLayout(graph_layout)
        
        self.plot = Graph()
        self.toolbar = NavigationToolbar(self.plot, parent=None)
        graph_layout.addWidget(self.plot)
        graph_layout.addWidget(self.toolbar)
        
        ## buttons
        buttons = QtGui.QHBoxLayout()
        buttons.addStretch(1)
        right.addLayout(buttons)
        
        # generate graph
        generate = QtGui.QPushButton("Generate Graph")
        buttons.addWidget(generate)
        QtCore.QObject.connect(generate,
                QtCore.SIGNAL("clicked()"), self.generate_graph)
        
        ###
        
        # top level container
        top = QtGui.QHBoxLayout()
        top.addLayout(left)
        top.addLayout(right)
        self.setLayout(top)
        
        self.show()
    
    # generate a graph with inputs
    def generate_graph(self):
        
        new_graph = graph.graph_obj("Atmospheric Model", [])
        self.energy_form = self.energy_list[self.config_sets[1]["e_units"].widget.currentIndex()]
        
        # Atmospheric radiance
        if self.atmos_toplot[0].isChecked():
            # loop through all selected sites
            for group in self.atmos_collection:
                index = group.inputs["site"].widget.currentIndex()
                # only add to graph if a site is selected
                if index > 0:
                    generate.add_radiance(self, new_graph, self.atmos_files[index - 1])
        
        # Atmospheric transmission
        if self.atmos_toplot[1].isChecked():
            # loop through all selected sites
            for group in self.atmos_collection:
                index = group.inputs["site"].widget.currentIndex()
                # only add to graph if a site is selected
                if index > 0:
                    generate.add_trans(self, new_graph, self.atmos_files[index - 1])
        
        # Galactic emission
        if self.galactic_toplot.isChecked():
            # loop through all selected coordinates
            for group in self.galactic_collection:
                index = group.inputs["gcrd"].widget.currentIndex()
                # only add to graph if a coordinate is selected
                if index > 0:
                    generate.add_galactic(self, new_graph, self.galactic_files[index - 1])
        
        # Thermal mirror emission
        if self.mirror_toplot.isChecked():
            # loop through all selected mirror types
            for group in self.mirror_collection:
                
                try: # check if given temperature is a number
                    temp = float(group.inputs["temp"].widget.text())
                except ValueError:
                    continue # not filled in properly, so skip
                
                index = str(group.inputs["type"].widget.currentText())
                
                # only add to graph if a type is selected
                if len(index) > 0:
                    generate.add_mirror(self, new_graph, index,
                        temp, self.mirror_consts[index])
        
        # Zodiacal emission
        if self.zodiac_toplot.isChecked():
            # loop through all selected coordinates
            for group in self.zodiac_collection:
                index = group.inputs["ecrd"].widget.currentIndex()
                # only add to graph if a coordinate is selected
                if index > 0:
                    generate.add_zodiac(self, new_graph,
                        self.zodiac_files[index - 1])
        
        # Cosmic infrared background
        if self.other_toplot.isChecked() and self.other_set["cib"].widget.isChecked():
            generate.add_cib(self, new_graph)
        
        # Cosmic microwave background
        if self.other_toplot.isChecked() and self.other_set["cmb"].widget.isChecked():
            generate.add_cmb(self, new_graph)
        
        # Signal
        if self.signal_toplot.isChecked():
            # loop through all aperture/site/source sets
            for group in self.signal_collection:
                
                try: # check if given aperture is a number
                    aperture = float(group.inputs["aperture"].widget.text())
                except ValueError:
                    continue # not filled in properly, so skip
                
                site = group.inputs["site"].widget.currentIndex()
                source = group.inputs["source"].widget.currentIndex()
                
                # only add if all fields are filled in
                if site > 0 and source > 0:
                    generate.add_signal(self, new_graph,
                        aperture,
                        self.atmos_files[site - 1],
                        self.source_files[source - 1])
        
        # Composite calculations
        compos_plot = self.compos_whatbox.currentIndex()
        
        if compos_plot > 0:
            
            i = 0
            # loop through all sets of inputs
            for group in self.compos_collection:
                if group.inputs["is_plot"].widget.isChecked() != True:
                    continue # not selected for plotting
                if i == len(self.compos_collection) - 1:
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
                    atmos_index2 = self.atmos_collection[atmos_index1-1].inputs["site"].widget.currentIndex()
                    atmos_site = self.atmos_files[atmos_index2-1]
                
                # galactic emission
                galactic_index1 = group.inputs["n_galactic"].widget.currentIndex()
                if galactic_index1 > 0:
                    galactic_index2 = self.galactic_collection[galactic_index1-1].inputs["gcrd"].widget.currentIndex()
                    galactic = self.galactic_files[galactic_index2-1]
                
                # thermal mirror emission
                mirror_index = group.inputs["n_mirror"].widget.currentIndex()
                if mirror_index > 0:
                    type_index = str(self.mirror_collection[mirror_index-1].inputs["type"].widget.currentText())
                    
                    mirror_constant = self.mirror_consts[type_index]
                    try:
                        mirror_temp = float(self.mirror_collection[mirror_index-1].inputs["temp"].widget.text())
                    except Exception:
                        pass
                
                # zodiacal emission
                zodiac_index1 = group.inputs["n_zodiac"].widget.currentIndex()
                if zodiac_index1 > 0:
                    zodiac_index2 = self.zodiac_collection[zodiac_index1-1].inputs["ecrd"].widget.currentIndex()
                    zodiac = self.zodiac_files[zodiac_index2-1]
                    
                cib = group.inputs["o_cib"].widget.isChecked()
                cmb = group.inputs["o_cmb"].widget.isChecked()
                
                # signal
                signal_index = group.inputs["signal"].widget.currentIndex()
                if signal_index > 0:
                    site_index = self.signal_collection[signal_index-1].inputs["site"].widget.currentIndex()
                    source_index = self.signal_collection[signal_index-1].inputs["source"].widget.currentIndex()
                    
                    try:
                        aperture = float(self.signal_collection[signal_index-1].inputs["aperture"].widget.text())
                    except Exception:
                        pass
                    source = self.source_files[source_index-1]
                    if site_index > 0:
                        site = self.atmos_files[site_index-1] # override atmospheric radiance site if provided
                
                if compos_plot == 1: # total noise
                    generate.add_noise(self, new_graph, dataset_label, atmos_site,
                            galactic, mirror_temp, mirror_constant, zodiac, cib, cmb)
                
                elif compos_plot == 2: # total temperature
                    generate.add_temp(self, new_graph, dataset_label, atmos_site,
                            galactic, mirror_temp, mirror_constant, zodiac, cib, cmb,
                            aperture, site, source)
                
                elif compos_plot == 3: # integration time
                    
                    try: # check if given signal:noise ratio is a number
                        snr = float(group.inputs["snr"].widget.text())
                    except ValueError:
                        continue # not filled in properly, so skip
                
                    generate.add_integ(self, new_graph, dataset_label, atmos_site, galactic,
                            mirror_temp, mirror_constant, zodiac, cib, cmb, aperture,
                            site, source, snr)

        self.plot.redraw(new_graph)
