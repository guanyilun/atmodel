#!/usr/bin/env python

import os
import sys
from PyQt4 import QtGui

from gui import *
import bling

def add_files(file_list, directory):
    for obj in os.listdir(directory):
        # skip if file is not data
        if obj[obj.find(".")+1:len(obj)] != "xlsx":
            continue
        
        # shorten displayed name
        name = obj[0:obj.find(".")]
        if len(name) > 20:
            name = name[0:17] + "..."
        
        file_list.append(bling.name_file(name, directory + obj))

def main():
    
    app = QtGui.QApplication(sys.argv)
    
    # create name file pairs
    atmos_files = []
    add_files(atmos_files, "data/Backgrounds/Atmospheric sites/")
    
    source_files = []
    add_files(source_files, "data/Sources/")
        
    galactic_files = []
    add_files(galactic_files, "data/Backgrounds/Galactic Emission/")
    
    # material constants for thermal mirror emission
    mirror_consts = {"Aluminum (Al)" : 3.538e7,
                     "Beryllium (Be)": 2.500e7,
                     "Gold (Au)"     : 4.060e7,
                     "Silver (Ag)"   : 6.287e7}
    
    zodiac_files = []
    add_files(zodiac_files, "data/Backgrounds/Zodiacal Emission/")
    
    main_gui = gui(atmos_files, source_files, galactic_files, mirror_consts, zodiac_files)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
