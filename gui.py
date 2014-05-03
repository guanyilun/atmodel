# gui.py
# graphical interface

from PyQt4 import QtCore, QtGui
import collections

import dyngui

class gui(QtGui.QWidget):
    
    def __init__(self, sites, sources, glat, elat, mtypes):
        super(gui, self).__init__()
        self.sites_list = sites # list of observer sites
        self.sources_list = sources # list of source galaxies
        self.glat_list = glat # list of galactic latitudes
        self.elat_list = elat # list of ecliptic latitudes
        self.mtypes_list = mtypes # list of mirror types (metals)
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
        self.resize(900, 550)
        self.center()
        self.setWindowTitle("Atmospheric Modeling")
        
        ###
        ### Left Side (input settings)
        ###
        
        left = QtGui.QVBoxLayout()
        
        left_tabs = QtGui.QTabWidget()
        left_tabs.setTabPosition(QtGui.QTabWidget.North)
        left_tabs.setFixedWidth(400)
        left.addWidget(left_tabs, 0, QtCore.Qt.AlignLeft)
        
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
        ignored_value, self.atmos_list =  self.add_tab(
            noise_tabs, "Atmospheric", "Earth's Atmosphere", self.atmos_toplot)
        self.atmos_collection = []
        
        atmos_set0 = self.atmos_inputs()
        self.atmos_collection.append(dyngui.collect_obj(atmos_set0,
                dyngui.new_group(self.atmos_list, atmos_set0)))
        
        # Galactic Emission
        
        self.galactic_toplot, self.galactic_list = self.add_tab(noise_tabs, "Galactic", "Galactic Emission")
        self.galactic_collection = []
        
        galactic_set0 = self.galactic_inputs()
        self.galactic_collection.append(dyngui.collect_obj(galactic_set0,
                dyngui.new_group(self.galactic_list, galactic_set0)))
        
        # Thermal Mirror Emission
        
        self.mirror_toplot, self.mirror_list = self.add_tab(noise_tabs, "Mirror", "Thermal Mirror Emission")
        self.mirror_collection = []
        self.mirror_groups = []
        
        mirror_set0 = self.mirror_inputs()
        self.mirror_collection.append(dyngui.collect_obj(mirror_set0,
                dyngui.new_group(self.mirror_list, mirror_set0)))
        
        # Zodiacal Emission
        
        self.zodiac_toplot, self.zodiac_list = self.add_tab(noise_tabs, "Zodiacal", "Zodiacal Emission")
        self.zodiac_collection = []
        self.zodiac_groups = []
        
        zodiac_set0 = self.zodiac_inputs()
        self.zodiac_collection.append(dyngui.collect_obj(zodiac_set0,
                dyngui.new_group(self.zodiac_list, zodiac_set0)))
        
        # Other Noise
        
        self.other_toplot, other_list = self.add_tab(noise_tabs, "Other", "Other Noise")
        
        other_set = self.other_inputs()
        dyngui.new_group(other_list, other_set)
        
        ## -- SIGNAL -- ##
        
        self.signal_toplot, self.signal_list = self.add_tab(left_tabs, "Signal", "Signal")
        self.signal_collection = []
        self.signal_groups = []
        
        signal_set0 = self.signal_inputs()
        self.signal_collection.append(dyngui.collect_obj(signal_set0,
                dyngui.new_group(self.signal_list, signal_set0)))
        
        ## -- COMPOSITE -- ##
        
        compos_panel = QtGui.QWidget()
        left_tabs.addTab(compos_panel, "Composite")
        compos_layout = QtGui.QVBoxLayout()
        compos_panel.setLayout(compos_layout)
        compos_layout.addWidget(QtGui.QLabel("<h3>Composite</h3>"),
                0, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        
        # scroll area with control widgets
        self.compos_contain = QtGui.QScrollArea()
        compos_layout.addWidget(self.compos_contain)
        self.compos_clayout = QtGui.QFormLayout()
        self.compos_contain.setLayout(self.compos_clayout)
        self.compos_contain.setFrameShape(QtGui.QFrame.NoFrame) # don't show the border
        
        # collection of widgets
        self.compos_collection = []
        
        compos_set0 = self.compos_inputs()
        self.compos_collection.append(dyngui.collect_obj(compos_set0,
            dyngui.new_group(self.compos_clayout, compos_set0)))
        
        # what to plot
        compos_what = QtGui.QWidget()
        compos_layout.addWidget(compos_what, 0, QtCore.Qt.AlignHCenter)
        compos_whatlo = QtGui.QFormLayout()
        compos_what.setLayout(compos_whatlo)
        
        compos_whatbox = QtGui.QComboBox()
        compos_whatbox.addItem("None")
        compos_whatbox.addItem("Total Noise")
        compos_whatbox.addItem("Total Temperature")
        compos_whatbox.addItem("Integration Time")
        
        compos_whatlo.addRow("Plot:", compos_whatbox)
        
        ###
        ### Right Side (input settings)
        ###
        
        right = QtGui.QVBoxLayout()
        
        ## graph
        graph = QtGui.QVBoxLayout()
        graph.addStretch(1)
        right.addLayout(graph)
        
        ## input frequency range (domain)
        domain = QtGui.QHBoxLayout()
        domain.addStretch(1)
        right.addLayout(domain)
        
        # label for frequency
        domain.addWidget(QtGui.QLabel("Frequencies (THz): "))
        
        # min frequency
        self.freq_min = QtGui.QLineEdit()
        self.freq_min.setPlaceholderText("min")
        self.freq_min.setAlignment(QtCore.Qt.AlignHCenter)
        self.freq_min.setFixedWidth(80)
        domain.addWidget(self.freq_min)
        
        # to frequnecy label
        domain.addWidget(QtGui.QLabel(" to "))
        
        # max frequency
        self.freq_max = QtGui.QLineEdit()
        self.freq_max.setPlaceholderText("max")
        self.freq_max.setAlignment(QtCore.Qt.AlignHCenter)
        self.freq_max.setFixedWidth(80)
        domain.addWidget(self.freq_max)
        
        # use default (maximum) range
        def auto_box_update(use_auto):
            self.freq_max.setReadOnly(use_auto)
            self.freq_min.setReadOnly(use_auto)
        
        self.auto_domain = QtGui.QCheckBox("Auto")
        QtCore.QObject.connect(self.auto_domain,
                QtCore.SIGNAL("toggled(bool)"), auto_box_update)
        self.auto_domain.setCheckState(QtCore.Qt.Checked)
        domain.addWidget(self.auto_domain)
        
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
        freq_min = self.freq_min.text()
        freq_max = self.freq_max.text()
        
        atmos_site = self.atmos_collection[0]["site"].widget.currentIndex()
        galactic_lat = self.galactic_collection[0]["glat"].widget.currentIndex()
        mirror_temp = float(self.mirror_collection[0]["temp"].widget.text())
        mirror_type = self.mirror_collection[0]["type"].widget.currentIndex()
        zodiac_lat = self.zodiac_collection[0]["eclat"].widget.currentIndex()
        other_cmb = self.cmb_collection[0]["cmb"].widget.checkState()
        
    # add new tab page of inputs
    def add_tab(self, parent, label, heading, to_plot_list = {}):
        
        # create actual tab page
        tab = QtGui.QWidget()
        parent.addTab(tab, label)
        
        # setup layout of tab page
        layout = QtGui.QVBoxLayout()
        tab.setLayout(layout)
        
        # show a heading for the tab if one is given
        if heading != None:
            layout.addWidget(QtGui.QLabel("<h3>" + heading + "</h3>"), 0, QtCore.Qt.AlignHCenter)
        
        # checkbox to plot everything in current tab
        if len(to_plot_list) < 1:
            to_plot = QtGui.QCheckBox("Plot this data")
            to_plot.setCheckState(QtCore.Qt.Unchecked)
            layout.addWidget(to_plot, 0, QtCore.Qt.AlignHCenter)
        
        else: # show all plotting checkboxes if specified
            to_plot = None
            for checkbox in to_plot_list:
                layout.addWidget(checkbox, 0, QtCore.Qt.AlignHCenter)
        
        # scroll area to contain possible overflow of input controls
        scroll = QtGui.QScrollArea()
        layout.addWidget(scroll)
        
        # list of groups of input controls
        control_list = QtGui.QFormLayout()
        scroll.setLayout(control_list)
        scroll.setFrameShape(QtGui.QFrame.NoFrame) # don't show the border
        
        return (to_plot, control_list) # allow groups of controls to be added later
        
    # connect widgets to update function
    def conn_update(self, widget, sig):
        QtCore.QObject.connect(widget, QtCore.SIGNAL(sig), self.update_all)
        
    ###
    ### Various input settings
    ###
    
    # Atmospheric Radiance
    def atmos_inputs(self):
        
        inputs = {}
        site = QtGui.QComboBox()
        site.addItem("")
        site.addItems(self.sites_list)
        self.conn_update(site, "currentIndexChanged(int)")
        inputs["site"] = dyngui.input_obj("Site", site)
        
        return inputs
    
    # Galactic Emission
    def galactic_inputs(self):
        
        inputs = {}
        
        latitude = QtGui.QComboBox()
        latitude.addItem("")
        latitude.addItems(self.glat_list)
        self.conn_update(latitude, "currentIndexChanged(int)")
        inputs["glat"] = dyngui.input_obj("Galactic Latitude", latitude)
        
        return inputs
    
    # Thermal Mirror Emission
    def mirror_inputs(self):
        
        inputs = {}
        
        inputs["temp"] = dyngui.input_obj("Temperature (K)", QtGui.QLineEdit())
        self.conn_update(inputs["temp"].widget, "textChanged(QString)")
        
        mirror_type = QtGui.QComboBox()
        mirror_type.addItem("")
        mirror_type.addItems(self.mtypes_list)
        self.conn_update(mirror_type, "currentIndexChanged(int)")
        inputs["type"] = dyngui.input_obj("Mirror Type", mirror_type)
        
        return inputs
        
    # Zodiacal Emission
    def zodiac_inputs(self):
        
        inputs = {}
        
        latitude = QtGui.QComboBox()
        latitude.addItem("")
        latitude.addItems(self.elat_list)
        self.conn_update(latitude, "currentIndexChanged(int)")
        inputs["eclat"] = dyngui.input_obj("Ecliptic Latitude", latitude)
        
        return inputs
    
    # Other Noise
    def other_inputs(self):
        
        inputs = {}
        cib = QtGui.QCheckBox("Cosmic Infrared Background")
        cib.setCheckState(QtCore.Qt.Checked)
        cmb = QtGui.QCheckBox("Cosmic Microwave Background")
        cmb.setCheckState(QtCore.Qt.Checked)
        inputs["cib"] = dyngui.input_obj("", cib)
        inputs["cmb"] = dyngui.input_obj("", cmb)
        
        return inputs
        
    # Signal
    def signal_inputs(self):
        
        inputs = {}
        
        inputs["aper"] = dyngui.input_obj("Aperture (m)", QtGui.QLineEdit())
        self.conn_update(inputs["aper"].widget, "textChanged(QString)")
        
        site = QtGui.QComboBox()
        site.addItem("")
        site.addItems(self.sites_list)
        self.conn_update(site, "currentIndexChanged(int)")
        inputs["site"] = dyngui.input_obj("Site", site)
        
        source = QtGui.QComboBox()
        source.addItem("")
        source.addItems(self.sources_list)
        self.conn_update(source, "currentIndexChanged(int)")
        inputs["source"] = dyngui.input_obj("Source", source)
        
        return inputs
        
    # Composite Data Calculations
    def compos_inputs(self):
        
        inputs = {}
        
        # initialize drop down boxes
        atmos = QtGui.QComboBox()
        dyngui.update_list(atmos, self.atmos_collection)
        self.conn_update(atmos, "currentIndexChanged(int)")
        
        galactic = QtGui.QComboBox()
        dyngui.update_list(galactic, self.galactic_collection)
        self.conn_update(galactic, "currentIndexChanged(int)")
        
        mirror = QtGui.QComboBox()
        dyngui.update_list(mirror, self.mirror_collection)
        self.conn_update(mirror, "currentIndexChanged(int)")
        
        zodiac = QtGui.QComboBox()
        dyngui.update_list(zodiac, self.zodiac_collection)
        self.conn_update(zodiac, "currentIndexChanged(int)")
        
        signal = QtGui.QComboBox()
        dyngui.update_list(signal, self.signal_collection)
        self.conn_update(signal, "currentIndexChanged(int)")
        
        inputs["n_atmos"] = dyngui.input_obj("Atmospheric", atmos)
        inputs["n_galactic"] = dyngui.input_obj("Galactic", galactic)
        inputs["n_mirror"] = dyngui.input_obj("Mirror", mirror)
        inputs["n_zodiac"] = dyngui.input_obj("Zodiacal", zodiac)
        inputs["signal"] = dyngui.input_obj("Signal", signal)
        inputs["snr"] = dyngui.input_obj("Signal:Noise", QtGui.QLineEdit())
        inputs["z_clear"] = dyngui.input_obj("", QtGui.QPushButton("Clear Fields"))
        inputs["z_default"] = dyngui.input_obj("", QtGui.QPushButton("Use Default"))
        
        return inputs
        
    # Propogate changes by updating all dynamic elements
    def update_all(self):
        
        # update all collections of widget groups
        dyngui.update_collection(self.atmos_collection, self.atmos_list, self.atmos_inputs)
        dyngui.update_collection(self.galactic_collection, self.galactic_list, self.galactic_inputs)
        dyngui.update_collection(self.mirror_collection, self.mirror_list, self.mirror_inputs)
        dyngui.update_collection(self.zodiac_collection, self.zodiac_list, self.zodiac_inputs)
        dyngui.update_collection(self.signal_collection, self.signal_list, self.signal_inputs)
        dyngui.update_collection(self.compos_collection, self.compos_clayout, self.compos_inputs)
        
        # update composite tab
        for group in self.compos_collection:
            dyngui.update_list(group.inputs["n_atmos"].widget, self.atmos_collection)
            dyngui.update_list(group.inputs["n_galactic"].widget, self.galactic_collection)
            dyngui.update_list(group.inputs["n_mirror"].widget, self.mirror_collection)
            dyngui.update_list(group.inputs["n_zodiac"].widget, self.zodiac_collection)
            dyngui.update_list(group.inputs["signal"].widget, self.signal_collection)
