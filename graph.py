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
graph_obj = collections.namedtuple("graph_obj", "title dataset_list")

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

        #clear figure
        plt.clf()
        
        # store all graph data for future use
        self.graph_data = graph_data

        #define axes
        self.axes = self.figure.add_subplot(111)

        data = graph_data.dataset_list

        #check to make sure there aren't too many data sets
        if len(data) > 6:
            print("Error: Tried to plot more than six data sets")
            return
        #sort data by units and also make sure there aren't too many units
        for n in xrange(len(data)):
            if n == 0:
                set0 = [data[n]]
                set1 = []
            elif data[n].xunits != set0[0].xunits:
                print("Error: Tried to plot more than one set of units on xaxis")
                return
            elif data[n].yunits != data[0].yunits:
                if len(set1) == 0:
                    set1.append(data[n])
                elif data[n].yunits != set1[0].yunits:
                    print("Error: Tried to plot more than two sets of units on yaxis")
                    return
                else:
                    set1.append(data[n])
            else:
                set0.append(data[n])

        #colors to give to plots
        color_list=['r','g','b','m','c','k']

        #setting default scale to log and plotting data
        self.axes.set_xscale('log')
        self.axes.set_yscale('log')
        for n in xrange(len(set0)):
            self.x = [set0[n].coord_list[i][0] for i in xrange(len(set0[n].coord_list))]
            self.y = [set0[n].coord_list[i][1] for i in xrange(len(set0[n].coord_list))]
            self.axes.plot(self.x, self.y, c=color_list[n], label=str(set0[n].label))

        #axis labels
        self.axes.set_xlabel(set0[0].xname + ' (' + set0[0].xunits + ')')
        self.axes.set_ylabel(set0[0].yname + ' (' + set0[0].yunits + ')')
        self.axes.set_xscale('log')
        self.axes.set_yscale('log')

        if len(set1) > 0:

            #define twin axes
            twinx = self.axes.twinx()

            #plot on twin axes
            for n in xrange(len(set1)):
                self.x = [set1[n].coord_list[i][0] for i in xrange(len(set1[n].coord_list))]
                self.y = [set1[n].coord_list[i][1] for i in xrange(len(set1[n].coord_list))]
                twinx.plot(self.x, self.y, c=color_list[n+len(set0)], label=str(set1[n].label))

            #name and scale twin axes
            twinx.set_ylabel(set1[0].yname + ' (' + set1[0].yunits + ')')
            twinx.set_yscale('log')

            #making legends (they will never die)
            leg2 = twinx.legend(loc='lower right',prop={'size':7})
            frame2 = leg2.get_frame()
            frame2.set_alpha(0.5)

        leg1 = self.axes.legend(loc='lower left',prop={'size':7})
        frame1 = leg1.get_frame()
        frame1.set_alpha(0.5)
        
        # set title of graph
        self.axes.set_title(graph_data.title)

        #draw new graph
        self.draw()

    # Update the graph title
    def set_title(self, new_title):
        
        # only update title if graph is not empty
        if hasattr(self, "graph_data"):
            
            self.axes.set_title(new_title)
            self.graph_data = graph_obj(new_title, self.graph_data.dataset_list)
            self.draw()

    # Export data current on the graph to a file
    def export(self, file_path):
        
        # only export data from graph if the graph exists
        if hasattr(self, "graph_data"):
            
            # TODO: export the data
            None
