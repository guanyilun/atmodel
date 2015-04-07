# interpolate.py
# create and manage data sets

import math
import numpy as np
from operator import itemgetter
from scipy.interpolate import interp1d

import auxil
import cal
import const

class Interpolate:

    def __init__ (self, freq_range, divisions = 1000):
        self.set_freq_hz (freq_range, divisions)

    # update frequency interval and spacing
    def set_freq_hz (self, freq_range, divisions = 1000):
        self.freq_range = freq_range
        self.divisions = divisions

        # compute list of frequencies
        self.freq_list = [freq_range.min]
        lnspace = (math.log(freq_range.max) - math.log(freq_range.min)) / divisions

        for i in range(1, divisions):
            self.freq_list.append(math.exp(math.log(freq_range.min) + i * lnspace))

        self.freq_array = np.array(self.freq_list)
        return self.freq_list

    # update frequency interval with wavelength
    def set_wl_m (self, wl_range, divisions = 1000):
        self.freq_range = \
            auxil.interval(const.c / wl_range.max, const.c / wl_range.min)
        self.divisions = divisions

        # compute list of frequencies with even wavelength spacing
        self.freq_list = [self.freq_range.min]
        lnspace = (math.log(wl_range.max) - math.log(wl_range.min)) / divisions

        for i in range(1, divisions):
            self.freq_list.append(const.c / math.exp(math.log(wl_range.min) + i * lnspace))
        self.freq_list.sort()

        self.freq_array = np.array(self.freq_list)
        return self.freq_list

    # create data set interpolated to defined set of frequencies
    #  --> new_data : list of interpolated points such that
    #                 (freq, data) => (self.freq_list, new_data)
    def interpolate (self, freq, data):

        # sort in monotonically ascending order with no duplicate frequencies
        if len(freq) > 0:
            freq, data = auxil.unique_freq(*(
                list(x) for x in zip(*sorted(zip(freq, data),
                key=lambda pair: pair[0]))))

            # remove zero frequency lines
            while freq[0] == 0:
                freq.remove(freq[0])
                data.remove(data[0])

        # define interpolation function
        f = cal.interp_or_zero(freq, data)

        # create new list of dependent coordinates
        new_data = []

        for x in self.freq_list:
            new_data.append(f(x))

        return new_data
