# sigtrans.py
# process signal and transmission data

from excel import ExcelXWriter, ExcelReader
import math
import numpy

import auxil as aux
import cal
import graph

# Atmospheric Transmission
def trans(gui, site_file):
    if not site_file: # return full transmission (ie. space) if no site given
        return numpy.array(aux.get_one(gui.interp.freq_list))

    site = ExcelReader(site_file)
    freq_raw = numpy.array(site.read_from_col('Hz',
            gui.interp.freq_range.min, gui.interp.freq_range.max), dtype='float')
    trans_raw = numpy.array(site.read_from_col(0,
            gui.interp.freq_range.min, gui.interp.freq_range.max, 'COMBIN TRANS'), dtype='float')

    return gui.interp.interpolate(freq_raw.tolist(), trans_raw.tolist())

# Compute Signal
def signal(gui, aperture, site_file, source_file, spec_res):

    source = ExcelReader(source_file)
    freq_raw = numpy.array(source.read_from_col('Hz',
        gui.interp.freq_range.min, gui.interp.freq_range.max), dtype='float')

    intens_raw = 1e-26 * numpy.array(source.read_from_col('Jy',
        gui.interp.freq_range.min, gui.interp.freq_range.max), dtype='float')

    intensity = gui.interp.interpolate(freq_raw.tolist(), intens_raw.tolist())
    trans_list = trans(gui, site_file)

    return cal.TS(gui.interp.freq_array, intensity, trans_list, aperture, spec_res)
