# graph.py
# graph widget

from PyQt4 import QtCore, QtGui
import numpy as np
import collections
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

#this is only here fore the placeholder data test
import random

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

class Graph(FigureCanvas):
    def __init__(self):
        #initializing the canvas
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)

    #this happens every time Generate is clicked
    def redraw(self, graph_data):
        #define axes
        self.axes = self.figure.add_subplot(111)
        
        #remove old graph
        self.axes.hold(False)
        
        #placeholder data to check that this works
        self.x = np.arange(0.0, 3.0, 0.01)
        self.y = random.random()*np.sin(2*np.pi*self.x)
        self.axes.plot(self.x, self.y)
        
        #draw new graph
        self.draw()

