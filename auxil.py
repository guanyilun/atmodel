# aux.py
# Library of auxiliary functions and other objects

import collections
from excel import ExcelXWriter, ExcelReader
import numpy

name_file = collections.namedtuple("name_file", "name file")
interval = collections.namedtuple("interval", "min max")
energy_form = collections.namedtuple("energy_form",
    "type units to_hz from_hz to_m is_freq")

# generate list of frequencies (in Hz) with identical form as data
def generate_freq(freq_range):
    step = 3e9 # increment (Hz)

    freq_min = 1.5e9 # minimum frequency
    freq_max = 1.64955e13 # maximum frequency
    if freq_range.min > freq_min:
        freq = int((freq_range.min - freq_min) / step + 1) * step + freq_min
    else: freq = freq_min

    freq_list = []
    zero_list = []
    while freq < freq_range.max - 1e-5 and freq < freq_max - 1e-5:
        freq_list.append(freq)
        zero_list.append(0)
        freq += step

    # convert to numpy arrays
    freq_array = numpy.array(freq_list, dtype="float")
    zero_array = numpy.array(zero_list, dtype="float")

    return freq_array, zero_array

# generate a zero list
def get_zero (freq_list):
    zero = []
    for freq in freq_list:
        zero.append(0)
    return zero

# generate a one list
def get_one (freq_list):
    one = []
    for freq in freq_list:
        one.append(1)
    return one

# Get column pair from data file
def get_col(file_name, col1, col1n, col2, col2n, freq_range):

    # convert to form understood by excel reader
    if col1n == 0:
        col1n = ' '
    if col2n == 0:
        col2n = ' '

    # read two columns from file and return them as numpy arrays
    data = ExcelReader(file_name)
    return [numpy.array(data.read_from_col(col1, freq_range.min, freq_range.max, col1n), dtype='float'),
        numpy.array(data.read_from_col(col2, freq_range.min, freq_range.max, col2n), dtype='float')]

# remove duplicate frequencies for frequency, data pairs
def unique_freq (freq, data):
    assert(len(freq) == len(data))
    new_freq = []
    new_data = []
    for i, freq_i in enumerate(freq):
        if freq_i not in new_freq:
            new_freq.append(freq_i)
            new_data.append(data[i])
    return new_freq, new_data

# return a function (fx) equivalent to another (func) being passed an argument (arg)
def func_arg(func, arg):

    def fx():
        return func(arg)

    return fx
