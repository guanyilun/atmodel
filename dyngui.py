# dyngui.py
# dynamical elements of the graphical interface

from PyQt4 import QtCore, QtGui
import collections

# set widgets in group and the group widget
collect_obj = collections.namedtuple("collect_obj", "inputs group_widget")

# line of input that user sees
input_obj = collections.namedtuple("input_obj", "label widget")

# add new group of input controls
def new_group(parent, inputs):
    
    # group of inputs
    group = QtGui.QGroupBox()
    group.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
    parent.addWidget(group)
    form = QtGui.QFormLayout()
    group.setLayout(form)
    
    # draw all specified input controls
    for key, line in iter(sorted(inputs.items())):
        line.widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        line.widget.setMinimumHeight(10)
        
        # display label only if one is given
        if line.label != "":
            form.addRow(QtGui.QLabel(line.label + ":"), line.widget)
        else:
            form.addRow(QtGui.QLabel(""), line.widget)
    return group

# New tab of input controls
def new_group_tab(parent, inputs, name):
    
    # group of inputs
    group = QtGui.QWidget()
    parent.addTab(group, name)
    form = QtGui.QFormLayout()
    group.setLayout(form)
    
    # draw all specified input controls
    for key, line in iter(sorted(inputs.items())):
        line.widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        line.widget.setMinimumHeight(10)
        
        # display label only if one is given
        if line.label != "":
            form.addRow(QtGui.QLabel(line.label + ":"), line.widget)
        else:
            form.addRow(QtGui.QLabel(""), line.widget)
    return group
    
    # add new tab page of inputs
def add_tab(parent, label, heading, to_plot_list = {}):
    
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
    
    # container holding input controls
    scroll = QtGui.QScrollArea()
    scroll.setFrameShape(QtGui.QFrame.NoFrame) # don't show the border
    layout.addWidget(scroll)
    
    # list of groups of input controls
    control_list = QtGui.QFormLayout()
    scroll.setLayout(control_list)
    
    return to_plot, control_list, layout # allow groups of controls to be added later

# Retrieve restorable value of a widget
def widget_val(widget):
    
    if hasattr(widget, "isChecked"):
        return widget.isChecked()
    
    if hasattr(widget, "currentIndex"):
        return widget.currentIndex()
    
    if hasattr(widget, "text"):
        return widget.text()
    
    return "" # return empty string by default

# Restore widget value retrieved earlier
def widget_val_restore(widget, value):
    
    if hasattr(widget, "setCheckState"):
        widget.setCheckState(value == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
    
    elif hasattr(widget, "setCurrentIndex"):
        try:
            widget.setCurrentIndex(int(value))
        except:
            pass
    
    elif hasattr(widget, "setText"):
        widget.setText(str(value))

# Return filled in value of a particular widget
def widget_str(widget, ignore_check = False):
    
    if hasattr(widget, "isChecked"):
        if not ignore_check:
            return widget.isChecked()
        elif widget.isChecked():
            return "True" # always recognize value of checkbox if checked
        else:
            return ""
    
    if hasattr(widget, "currentText"):
        return widget.currentText()
    
    if hasattr(widget, "text"):
        return widget.text()
    
    return "" # return empty string by default

# Generate a descriptor string from a group of widgets
def group_str(group, ignore_check = False):
    
    string = ""
    
    # loop through all the widgets, checking if they are filled in
    for name in iter(sorted(group)):
        
        if len(group[name].label) < 1 and not hasattr(group[name].widget, "isChecked"):
            continue # ignore widget if not labeled
        
        value = widget_str(group[name].widget, ignore_check)
        if len(str(value)) > 0:
            string += group[name].label + "=" + str(value) + "; "
    
    return string

# Update dropdown box with list of entered data
#  box: QComboBox to update_list
#  collection: collection of widget groups to retrieve data and update the box with
def update_list(box, collection):
    
    # if not enough elements, add more
    while box.count() < len(collection):
        box.addItem("")
    
    # if too many elements, remove the last one
    while box.count() > len(collection):
        box.removeItem(len(collection) - 1)
    
    # fill the elements with the descriptor text for each group of widgets
    box.setItemText(0, "")
    i = 1 # leave 0th element blank
    for group in collection:
        box.setItemText(i, group_str(group.inputs))
        i += 1

# Update collection of widget groups, removing and adding new groups on demand
#  collection: collection of widget groups to update
#  display_list: list of displayed widget groups
#  inputs_func: function that returns a set of widgets to add to the colllection
def update_collection(collection, display_list, inputs_func):
    
    to_remove = [] # list of groups to remove
    
    # loop through all existing widget groups in the collection
    i = 0
    n = len(collection) - 1 # index of last group, before removals
    
    for group in collection:
        
        # remove group if descriptor string is blank
        if group_str(group.inputs, True) == "" and i < n:
            group.group_widget.setParent(None) # prevent display
            group.group_widget.deleteLater() # remove from list of QGroupBox widgets
            collection.remove(group) # remove from collection
        
        i += 1
    
    k = len(collection) - 1 # index of last group of newly trimmed collection
    
    # add new group if last group is not empty
    if group_str(collection[k].inputs, True) != "":
        group_set = inputs_func() # generate a new set of widgets
        collection.append(collect_obj(group_set, new_group(display_list, group_set)))

# Update collection of tab widget collections, removing and adding new tabs on demand
#  collection: collection of widget groups to update
#  tabs_control: control that holds all the tabs
#  inputs_func: function that returns a set of widgets to add to the colllection
def update_tabcollect(collection, tab_control, inputs_func):
    
    to_remove = [] # list of groups to remove
    
    # loop through all existing widget groups in the collection
    i = 0
    n = len(collection) - 1 # index of last group, before removals
    
    for group in collection:
        
        label = group.inputs["_label"].widget.text()
        if len(label) > 0:
            tab_control.setTabText(i, label)
        else:
            tab_control.setTabText(i, "New")
        
        # remove group if descriptor string is blank
        if group_str(group.inputs, True) == "" and i < n:
            group.group_widget.setParent(None) # prevent display
            group.group_widget.deleteLater() # remove from list of QGroupBox widgets
            collection.remove(group) # remove from collection
        
        i += 1
    
    k = len(collection) - 1 # index of last group of newly trimmed collection
    
    # add new group if last group is not empty
    if group_str(collection[k].inputs, True) != "":
        group_set = inputs_func() # generate a new set of widgets
        collection.append(collect_obj(group_set, new_group_tab(tab_control, group_set, "New")))
