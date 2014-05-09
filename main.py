#!/usr/bin/env python

import os
import sys
from PyQt4 import QtGui

import generate
from gui import *

def add_files(file_list, directory):
    for obj in os.listdir(directory):
        # skip if file is not data
        if obj[obj.find(".")+1:len(obj)] != "xlsx":
            continue
        
        # shorten displayed name
        name = obj[0:obj.find(".")]
        if len(name) > 20:
            name = name[0:17] + "..."
        
        file_list.append(generate.name_file(name, directory + obj))

def main():
    
    app = QtGui.QApplication(sys.argv)
    
    # create name file pairs
    atmos_files = []
    add_files(atmos_files, "data/Backgrounds/Atmospheric Radiance_sites")
    
    source_files = []
    add_files(source_files, "data/Sources")
        
    galactic_files = []
    add_files(galactic_files, "data/Backgrounds/Galactic Emission")
    
    mirror_files = []
    add_files(mirror_files, "data/Backgrounds/Thermal Mirror Emission")
    
    zodiac_files = []
    add_files(zodiac_files, "data/Backgrounds/Zodiacal Emission")
    
    main_gui = gui(atmos_files, source_files, galactic_files, mirror_files, zodiac_files)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
