# run calculations in new thread
import sys, time
from PyQt4 import QtCore, QtGui

class Worker (QtCore.QObject):
    ready = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()

    def __init__ (self, main_thread):
        QtCore.QObject.__init__(self)
        self.main_thread = main_thread

    def update (self, func, gui):
        self.func = func
        self.gui = gui

    @QtCore.pyqtSlot()
    def run (self):
        self.new_graph = self.func(self.gui)
        self.ready.emit()
        self.moveToThread(self.main_thread)

    def get (self):
        return self.new_graph
