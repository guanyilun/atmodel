# sigtrans.py
# process signal and transmission data

from excel import ExcelXWriter, ExcelReader
import math
import numpy

import bling
import cal
import graph

# Atmospheric Transmission
def trans(site_file, freq_range):
    site = ExcelReader(site_file)
    return numpy.array(site.read_from_col(0, freq_range.min, freq_range.max, 'COMBIN TRANS'), dtype='float')

# Compute Signal
def signal(aperture, site_file, source_file, freq_range):
    
    source = ExcelReader(source_file)
    freq_list = numpy.array(source.read_from_col('Hz',freq_range.min, freq_range.max), dtype='float')
    intensity = numpy.array(source.read_from_col('W M-2 Hz-1', freq_range.min, freq_range.max), dtype='float')
    trans_list = trans(site_file, freq_range)
    
    return cal.TS(freq_list, intensity, trans_list, aperture, 1000), freq_list