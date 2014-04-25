 #!/usr/bin/env python
 
import sys
from PyQt4 import QtGui

from gui import *

# Observation sites
sites = ['13_7Km SOFIA', '30KmBalloon', '40KmBalloon', 'CCAT-0732g',
    'CCAT-0978g', 'DomeA-01g', 'DomeA-014g', 'DomeC-015g', 'DomeC-024g',
    'MaunaKea-1g', 'MaunaKea-15g', 'SantaBarbara-01g', 'SantaBarbara-30g',
    'SouthPole-023g','SouthPole-032g', 'WhiteMountain-115g',
    'WhiteMountain-175g',]

# Source galaxies    
sources = ['3C219', 'ARP220_z=1', 'M89', 'Maffei2', 'MRK231_z=1', 'NGC0315',
    'NGC262', 'NGC958_z=1', 'NGC1052', 'NGC1097', 'NGC1566', 'NGC3351',
    'NGC4725', 'NGC6764', 'NGC7793', 'NGC7832', 'PSRB0531-21', 'South America']

# Galactic and ecliptic latitudes
glat = ["0 degrees", "45 degrees", "90 degrees"]
elat = ["0 degrees", "45 degrees", "90 degrees"]

# Mirror types
mtypes = ["Aluminum (Al)", "Beryllium (Be)", "Gold (Au)", "Silver (Ag)"]

def main():
    
    app = QtGui.QApplication(sys.argv)
    
    main_gui = gui(sites, sources, glat, elat, mtypes)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
