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
        #self.x = np.arange(0.0, 3.0, 0.01)
        #self.y = random.random()*np.sin(2*np.pi*self.x)
        data = graph_data.dataset_list
        
        for n in xrange(len(data)):
            if n == 0:
                set0 = [data[n]]
                set1 = []
            elif data[n].xunits != set0[0].xunits:
                print("Tried to plot more than one set of units on xaxis")
                pass
            elif data[n].yunits != data[0].yunits:
                if len(set1) == 0:
                    set1.append(data[n])
                elif data[n].yunits != set1[0].yunits:
                    print("Tried to plot more than two sets of units on yaxis")
                else:
                    set1.append(data[n])
            else:
                set0.append(data[n])
        
        color_list=['r','g','b']
        print(len(data))
        print(len(set0))
        print(len(set1))
        print(set0[0].yunits)
        self.axes.set_xscale('log')
        self.axes.set_yscale('log')
        for n in xrange(len(set0)):
            self.x = [set0[n].coord_list[i][0] for i in xrange(len(set0[n].coord_list))]
            self.y = [set0[n].coord_list[i][1] for i in xrange(len(set0[n].coord_list))]
            self.axes.plot(self.x, self.y, c=color_list[n], label=data[n].label)
        self.axes.set_xlabel(set0[0].xunits)
        self.axes.set_ylabel(set0[0].yunits)
        self.axes.set_xscale('log')
        self.axes.set_yscale('log')

        #twinx = self.axes.twinx()
        #twinx.plot(self.x, self.y)
        
        #plt.xlabel(graph_data.dataset_list[0].xunits)
        #plt.ylabel(graph_data.dataset_list[0].yunits)
        plt.legend(loc='upper left')
        
        #draw new graph
        self.draw()

