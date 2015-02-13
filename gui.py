# gui.py
# graphical interface

import collections
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QTAgg as NavigationToolbar
import os
import sys

import auxil as aux
import config
import dyngui
import generate
import graph
from graph import *
import inputs
from interpolate import *
import project
import work

class gui(QtGui.QWidget):

    def __init__(self, energy_list, sites, source, galactic, mirror, zodiac):
        super(gui, self).__init__()

        self.energy_list = energy_list # ways of measuring photon energy
        self.atmos_files = sites # list of observer sites
        self.source_files = source # list of source galaxies
        self.galactic_files = galactic # list of galactic emission files
        self.mirror_consts = mirror # dictionary of constants for mirror types (metals)
        self.zodiac_files = zodiac # list of ecliptic emission files

        # Project settings
        self.interp = Interpolate(aux.interval(1e11, 1e13)) # frequency range (Hz)
        self.bling_units = 0 # use W/Hz^1/2 as default units of BLING
        self.noise_what = 0 # plot BLING by default for noise
        self.compos_what = 0 # plot total BLING by default for composite

        self.collections = {} # dictionary of collections of data input widgets
        self.groups = {} # dictionary of lone widget groups not part of a collection
        self.floating = {} # free-floating widgets not in any group or collection

        # calculation in separate worker thread
        self.main_thread = QtCore.QThread.currentThread()
        self.worker = work.Worker(self.main_thread)
        self.worker.ready.connect(self.done_work)

        self.init_UI()

        # Set default state
        self.changed = False # no edits made so far
        self.proj_file = "" # current project file path

        # Load project file if specified
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            project.open(self, sys.argv[1])

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

        self.config_sets = inputs.pconfig(self)
        for i, single_set in enumerate(self.config_sets):
             dyngui.new_group(config_controls, single_set)
             self.groups["config" + str(i)] = self.config_sets[i]

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
        self.floating["atmos_toplot0"] = self.atmos_toplot[0]
        self.floating["atmos_toplot1"] = self.atmos_toplot[1]
        self.atmos_list = dyngui.add_tab(
                noise_tabs, "Atmospheric", "Earth's Atmosphere", self.atmos_toplot)[1]
        self.atmos_collection = []

        atmos_set0 = inputs.atmos(self)
        self.atmos_collection.append(dyngui.collect_obj(atmos_set0,
                dyngui.new_group(self.atmos_list, atmos_set0)))
        self.collections["atmos"] = self.atmos_collection

        # Galactic Emission

        self.galactic_toplot, self.galactic_list, ign = dyngui.add_tab(noise_tabs, "Galactic", "Galactic Emission")
        self.floating["galactic_toplot"] = self.galactic_toplot
        self.galactic_collection = []

        galactic_set0 = inputs.galactic(self)
        self.galactic_collection.append(dyngui.collect_obj(galactic_set0,
                dyngui.new_group(self.galactic_list, galactic_set0)))
        self.collections["galactic"] = self.galactic_collection

        # Thermal Mirror Emission

        self.mirror_toplot, self.mirror_list, ign = dyngui.add_tab(noise_tabs, "Mirror", "Thermal Mirror Emission")
        self.floating["mirror_toplot"] = self.mirror_toplot
        self.mirror_collection = []
        self.mirror_groups = []

        mirror_set0 = inputs.mirror(self)
        self.mirror_collection.append(dyngui.collect_obj(mirror_set0,
                dyngui.new_group(self.mirror_list, mirror_set0)))
        self.collections["mirror"] = self.mirror_collection

        # Zodiacal Emission

        self.zodiac_toplot, self.zodiac_list, ign = dyngui.add_tab(noise_tabs, "Zodiacal", "Zodiacal Emission")
        self.floating["zodiac_toplot"] = self.zodiac_toplot
        self.zodiac_collection = []
        self.zodiac_groups = []

        zodiac_set0 = inputs.zodiac(self)
        self.zodiac_collection.append(dyngui.collect_obj(zodiac_set0,
                dyngui.new_group(self.zodiac_list, zodiac_set0)))
        self.collections["zodiac"] = self.zodiac_collection

        # Other Noise

        self.other_toplot, other_list, ign = dyngui.add_tab(noise_tabs, "Other", "Other Noise")
        self.floating["other_toplot"] = self.other_toplot

        self.other_set = inputs.other(self)
        dyngui.new_group(other_list, self.other_set)
        self.groups["other"] = self.other_set

        ## Bottom area
        noise_bottom = QtGui.QWidget()
        noise_layout.addWidget(noise_bottom, 0, QtCore.Qt.AlignHCenter)
        noise_botlo = QtGui.QFormLayout()
        noise_bottom.setLayout(noise_botlo)

        # spectral resolution for noise sources
        self.noise_res = QtGui.QLineEdit(config.spec_res)
        self.floating["noise_res"] = self.noise_res
        noise_botlo.addRow("Resolution:", self.noise_res)

        # what to plot (BLING or Temperature)
        self.noise_whatbox = QtGui.QComboBox()
        self.floating["noise_whatbox"] = self.noise_whatbox
        self.noise_whatbox.addItem("BLING")
        self.noise_whatbox.addItem("Temperature")

        noise_botlo.addRow("Plot:", self.noise_whatbox)

        ## -- SIGNAL -- ##

        self.signal_toplot, self.signal_list, signal_layout = dyngui.add_tab(left_tabs, "Signal", "Signal")
        self.floating["signal"] = self.signal_toplot
        self.signal_collection = []
        self.signal_groups = []

        signal_set0 = inputs.signal(self)
        self.signal_collection.append(dyngui.collect_obj(signal_set0,
                dyngui.new_group(self.signal_list, signal_set0)))
        self.collections["signal"] = self.signal_collection

        ## Bottom area
        signal_bottom = QtGui.QWidget()
        signal_layout.addWidget(signal_bottom, 0, QtCore.Qt.AlignHCenter)
        signal_botlo = QtGui.QFormLayout()
        signal_bottom.setLayout(signal_botlo)

        # spectral resolution for signal
        self.signal_res = QtGui.QLineEdit(config.spec_res)
        self.floating["signal_res"] = self.signal_res
        signal_botlo.addRow("Resolution:", self.signal_res)

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
        self.collections["compos"] = self.compos_collection

        # what to plot
        compos_what = QtGui.QWidget()
        compos_layout.addWidget(compos_what, 0, QtCore.Qt.AlignHCenter)
        compos_whatlo = QtGui.QFormLayout()
        compos_what.setLayout(compos_whatlo)

        self.compos_whatbox = QtGui.QComboBox()
        self.floating["compos_whatbox"] = self.compos_whatbox
        self.compos_whatbox.addItem("Total BLING")
        self.compos_whatbox.addItem("Total Temperature")
        self.compos_whatbox.addItem("Integration Time")

        compos_whatlo.addRow("Plot:", self.compos_whatbox)

        # changing value of widget causes project to be marked as changed
        for key, widget in self.floating.iteritems():

            if hasattr(widget, "currentIndex"):
                inputs.conn_changed(self, widget, "currentIndexChanged(int)")
            elif hasattr(widget, "checkState"):
                inputs.conn_changed(self, widget, "stateChanged(int)")
            elif hasattr(widget, "text"):
                inputs.conn_changed(self, widget, "textChanged(QString)")

        ###
        ### Right Side (input settings)
        ###

        right = QtGui.QVBoxLayout()

        ## menu bar
        menu_layout = QtGui.QVBoxLayout()
        right.addLayout(menu_layout)

        menu = QtGui.QToolBar()
        menu_layout.addWidget(menu)

        # create new project
        def new_proj ():
            # check for changes
            if self.changed: # ask to save existing project
                self.close_project(lambda: project.new(self), lambda: None)
            else: # no changes to be saved -> just open new project
                project.new(self)

        newprj = QtGui.QAction("&New", self)
        newprj.setToolTip("Reset interface")
        newprj.setShortcut("Ctrl+N")
        newprj.triggered.connect(new_proj)
        menu.addAction(newprj)

        # open project file
        def open_proj ():
            proj_file = QtGui.QFileDialog.getOpenFileName(self, "Open Project",
                    filter="Atmospheric Modeling Project (*.atmodel)")
            if len(proj_file) > 0: # open project file if a file is selected
                project.open(self, proj_file)

        def open_func ():
            # check for changes to existing project first
            if self.changed: # ask to save existing project
                self.close_project(open_proj, lambda: None)
            else: # no changes to be saved -> just open new project
                open_proj()

        openprj = QtGui.QAction("&Open", self)
        openprj.setToolTip("Open project file")
        openprj.setShortcut("Ctrl+O")
        openprj.triggered.connect(open_func)
        menu.addAction(openprj)

        # save project file
        def save_func ():
            if len(self.proj_file) > 0: # currently editing a project already
                project.save(self, self.proj_file)
            else: # no project file opened -- ask for file name
                saveas_func()

        saveprj = QtGui.QAction("&Save", self)
        saveprj.setToolTip("Save project file")
        saveprj.setShortcut("Ctrl+S")
        saveprj.triggered.connect(save_func)
        menu.addAction(saveprj)

        # save project file with different name
        def saveas_func ():
            proj_file = QtGui.QFileDialog.getSaveFileName(self, "Save Project",
                    filter="Atmospheric Modeling Project (*.atmodel)")
            if len(proj_file) > 0: # save project file if a name is selected
                project.save(self, proj_file)

        saveas = QtGui.QAction("Save As", self)
        saveas.setToolTip("Save project file with different name")
        saveas.triggered.connect(saveas_func)
        menu.addAction(saveas)

        # export data
        def export_func ():

            # allow data export only if graph exists
            if hasattr(self.plot, "graph_data"):
                export_file = QtGui.QFileDialog.getSaveFileName(self, "Export Data",
                    filter="Excel Spreadsheet (*.xlsx)")
                self.plot.export(export_file)

        export = QtGui.QAction("Export", self)
        export.setToolTip("Export data in graph")
        export.triggered.connect(export_func)
        menu.addAction(export)

        ## main graph + buttons
        self.plot = Graph()
        right.addWidget(self.plot)

        # buttons
        buttons = QtGui.QGridLayout() #QtGui.QHBoxLayout()
        right.addLayout(buttons)

        # generate graph
        self.gen_btn = QtGui.QPushButton("Generate Graph")
        self.gen_btn.setStyleSheet("background-color: #ffffff; font-weight: bold; height: 1.8em")
        buttons.addWidget(self.gen_btn, 1, 0)

        def do_generate ():
            # start calculations
            self.thread = QtCore.QThread()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.update(generate.process, self)
            self.thread.start()

            # do interface changes to notify of work in progress
            self.in_progress.setText("Working...")
            self.gen_btn.setEnabled(False)

        QtCore.QObject.connect(self.gen_btn,
                QtCore.SIGNAL("clicked()"), do_generate)

        # label stating "in progress"
        self.in_progress = QtGui.QLabel()
        # give this cell extra column space to no push the navbar
        buttons.addWidget(self.in_progress, 1, 1, 1, 13)

        # add toolbar for graph
        self.toolbar = NavigationToolbar(self.plot, parent=None)
        buttons.addWidget(self.toolbar, 1, 14)

        ###

        # top level container
        top = QtGui.QHBoxLayout()
        top.addLayout(left)
        top.addLayout(right)
        self.setLayout(top)

        self.show()

    # done generating graph
    def done_work (self):
        try:
            new_graph = self.worker.get()
            self.plot.redraw(new_graph)
            self.thread.quit()
            self.in_progress.clear()
        except Exception as e:
            self.in_progress.setText(str(e))

        # restore interface
        self.gen_btn.setEnabled(True)

    # Closing current project
    def close_project(self, accept_func, ignore_func):

        # check if there are unsaved changes
        if self.changed:
            reply = QtGui.QMessageBox.question(self, "Save Unsaved Changes?",
                "You have made unsaved changes to your project. Would you like to save them?",
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)

            # save project
            if reply == QtGui.QMessageBox.Yes:
                if len(self.proj_file) > 0: # currently editing a project already
                    project.save(self, self.proj_file)
                    accept_func()
                else: # no project file opened -- ask for file name
                    proj_file = QtGui.QFileDialog.getSaveFileName(self, "Save Project",
                            filter="Atmospheric Modeling Project (*.atmodel)")
                    if len(proj_file) > 0: # save project file if a name is selected
                        project.save(self, proj_file)
                        accept_func()
                    else: # no file name selected
                        ignore_func()

            # don't save project and quit
            elif reply == QtGui.QMessageBox.No:
                accept_func()

            # don't close the window
            else:
                ignore_func()

    # Window close event
    def closeEvent(self, event):
        self.close_project(event.accept, event.ignore)
