# graph.py
# graph widget

from PyQt4 import QtCore, QtGui
import collections

# object that defines a particular graph that is passed to the graph widget
#  title: title to be shown at top of graph
#  dataset_list: list of zero or more data_set objects
graph_obj = collections.namedtuple("graph_obj",
        "title dataset_list")

# individual data set to be graphed
#  label: description for data set to be shown in legend
#  xname: description of x coordinates
#  xunits: units of x coordinates
#  yname: description of y coordinates
#  yunits: units of y coordinates
#  coord_list: list of zero or more coordinate pairs
data_set = collections.namedtuple("data_set",
        "label xname xunits yname yunits coord_list")

# a single coordinate pair
coord_obj = collections.namedtuple("coord_obj", "x y")
