# sigtrans.py
# process signal and transmission data

from excel import ExcelXWriter, ExcelReader
import math
import numpy

import cal
import graph

# Atmospheric Transmission
def trans(site_file, freq_range):
    site = ExcelReader(site_file)
    freq_list = numpy.array(site.read_from_col('Hz',freq_range.min, freq_range.max), dtype='float')
    return numpy.array(site.read_from_col(0, freq_range.min, freq_range.max, 'COMBIN TRANS'), dtype='float'), freq_list

# Compute Signal
def signal(aperture, site_file, source_file, freq_range):
    
    source = ExcelReader(source_file)
    freq_list = numpy.array(source.read_from_col('Hz',freq_range.min, freq_range.max), dtype='float')
    intensity = numpy.array(source.read_from_col('W M-2 Hz-1', freq_range.min, freq_range.max), dtype='float')
    trans_list, fl2 = trans(site_file, freq_range)
    print len(freq_list),len(trans_list)
    return cal.TS(freq_list, intensity, trans_list, aperture, 1000), freq_list
