# dyngui.py
# dynamical elements of the graphical interface

from PyQt4 import QtCore, QtGui
import collections

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
        
        # display label only if one is given
        if line.label != "":
            form.addRow(QtGui.QLabel(line.label + ":"), line.widget)
        else:
            form.addRow(QtGui.QLabel(""), line.widget)

# Return filled in value of a particular widget
def widget_val(widget):
    
    if hasattr(widget, "currentText"):
        return widget.currentText()
    
    if hasattr(widget, "text"):
        return widget.text()
    
    if hasattr(widget, "checkState"):
        return widget.checkState() == QtCore.Qt.Checked

# Generate a descriptor string from a group of widgets
def group_str(group):
    
    string = ""
    
    # loop through all the widgets, checking if they are filled in
    for name in iter(sorted(group)):
        value = widget_val(group[name].widget)
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
    i = 0 # (change to 1 later)
    for group in collection:
        box.setItemText(i, group_str(group))
        i += 1
