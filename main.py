#!/usr/bin/env python

import os
import sys
from PyQt4 import QtGui

import auxil as aux
import const
from gui import gui

def add_files(file_list, directory):
    for obj in sorted(os.listdir(directory)):
        # skip if file is not data
        if obj[obj.find(".")+1:len(obj)] != "xlsx":
            continue

        # shorten displayed name
        name = obj[0:obj.find(".")]
        if len(name) > 20:
            name = name[0:17] + "..."

        file_list.append(aux.name_file(name, directory + obj))

def main():

    app = QtGui.QApplication(sys.argv)

    # convert from units of photon energy to frequency in Hz
    def freq_hz1 (hz): # frequency (Hz)
        return hz
    def freq_thz1 (thz): # frequency (THz)
        return 1e12 * thz
    def wl_m1 (m): # wavelength (m)
        return const.c / m
    def wl_microns1(um): # wavelength (microns)
        return const.c / (1e-6 * um)
    def wl_nm1 (nm): # wavelength (nm)
        return const.c / (1e-9 * nm)
    def wn_m_inv1 (m_inv): # wavenumber (m^-1)
        return const.c * m_inv
    def wn_cm_inv1 (cm_inv): # wavenumber (cm^-1)
        return const.c * (1e-2 * cm_inv)

    # convert from frequency in Hz to units of photon energy
    def freq_hz2 (hz): # frequency (Hz)
        return hz
    def freq_thz2 (hz): # frequency (THz)
        return 1e-12 * hz
    def wl_m2 (hz): # wavelength (m)
        return const.c / hz
    def wl_microns2 (hz): # wavelength (microns)
        return 1e6 * const.c / hz
    def wl_nm2 (hz): # wavelength (nm)
        return 1e9 * const.c / hz
    def wn_m_inv2 (hz): # wavenumber (m^-1)
        return hz / const.c
    def wn_cm_inv2 (hz): # wavenumber (cm^-1)
        return 1e2 * hz / const.c

    # convert from units of photon energy to wavelength in m
    def freq_hz3 (hz): # frequency (Hz)
        return const.c / hz
    def freq_thz3 (thz): # frequency (THz)
        return const.c / (1e12 * thz)
    def wl_m3 (m): # wavelength (m)
        return m
    def wl_microns3(um): # wavelength (microns)
        return 1e-6 * um
    def wl_nm3 (nm): # wavelength (nm)
        return 1e-9 * nm
    def wn_m_inv3 (m_inv): # wavenumber (m^-1)
        return 1.0 / m_inv
    def wn_cm_inv3 (cm_inv): # wavenumber (cm^-1)
        return 1.0 / (1e-2 * cm_inv)

    energy_list = \
        [aux.energy_form("Frequency", "Hz", freq_hz1, freq_hz2, freq_hz3, True),
         aux.energy_form("Frequency", "THz", freq_thz1, freq_thz2,
                                             freq_thz3, True),
         aux.energy_form("Wavelength", "m", wl_m1, wl_m2, wl_m3, False),
         aux.energy_form("Wavelength", "microns", wl_microns1, wl_microns2,
                                                  wl_microns3, False),
         aux.energy_form("Wavelength", "nm", wl_nm1, wl_nm2, wl_nm3, False),
         aux.energy_form("Wavenumber", "m^-1", wn_m_inv1, wn_m_inv2,
                                               wn_m_inv3, True),
         aux.energy_form("Wavenumber", "cm^-1", wn_cm_inv1, wn_cm_inv2,
                                                wn_cm_inv3, True)]

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

    main_gui = gui(energy_list, atmos_files, source_files, galactic_files,
                   mirror_consts, zodiac_files)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
