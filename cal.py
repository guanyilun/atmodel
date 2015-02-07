import gc, const
import math
import numpy as np
from scipy import integrate, interpolate
from excel import ExcelReader

cmb_temp = 2.725 # temperature of CMB (in K)
step_size_k = 1e-7

# These calculations reference equations in 2 papers:
# "Limitations on Observing Submillimeter and Far Infrared Galaxies" by Denny
# and "Fundamental Limits of Detection in the Far Infrared" by Denny et al

# calculate BLING^2 for a list of frequencies and a temperature function
def bling_sq (freq, temp_func, resol, polar_modes=2):
    bsq = []
    for freq_i in freq:
        # bling^2 = 2*h*k_b*int(freq*temp(freq))
        bsq.append(polar_modes * const.h * const.k * integrate.quad(
            lambda f: f * temp_func(f),
            freq_i - 0.5 * freq_i / float(resol),
            freq_i + 0.5 * freq_i / float(resol))[0])
    return bsq

# calculate BLING^2 for CIB, Galactic and Zodiacal Emission
def bling_sub (freq, temp, resol):

    # interpolant of provided mesh function
    temp_func = interpolate.interp1d(freq, temp, bounds_error=False)
    return bling_sq(freq, temp_func, resol, polar_modes=2)


# calculate BLING^2 for CMB (assume Planck distribution)
def bling_CMB (freq, resol):

    # assume Planck distribution for CMB temperature
    #   inten = 2*h*freq^3/c^2 * 1/(exp((h*freq)/(k*T))-1)
    #   temp = 1/2 * inten * c^2/(k*freq^2)
    #        = h*freq / [k * (exp((h*freq)/(k*T))-1)]
    cmb_tmp_distr = lambda f: const.h * f / \
            (const.k * (math.exp(const.h * f / (const.k * cmb_temp)) - 1))

    # compute BLING using analytic Planck distribution for temperature
    return bling_sq(freq, lambda f: f * cmb_temp_distr(f), resol, polar_modes=2)


# calculate BLING^2 for atmospheric radiance
def bling_AR (freq, rad, resol):

    # continuous interpolant function for radiance
    rad = rad / 3e6 # convert from W/cm^2/sr/cm^-1 to W/m^2/st/Hz
    rad_func = interpolate.interp1d(freq, rad, bounds_error=False)

    # calculate temperature at a frequency from radiance
    temp_func = lambda f: 0.5 * rad_func(f) * const.c**2 / (const.k * f**2)
    return bling_sq(freq, temp_func, resol, polar_modes=1)


def bling_TME(freq, resol, sigma, mirror_temp, wavelength):  #calculates BLING(squared) for "Thermal Mirror Emission"
##    What will be done: 1) Calculate emissivity from surface electrical conductivity("sigma") of specific metal
##                       1) Calculate effective temperature from emissivity and mirror temperature
##                       2) Calculate BLING(squared) from effective temperature
## 1) Calculate emissivity from surface electrical conductivity("sigma") of specific metal
    em = []  #create list to be filled with emissivities, depending on wavelength
    w_l = wavelength * (1e-6)  #convert wavelength from microns to meters
    c1 = 16 * np.pi * const.c * const.eps0 / sigma  #constants from equation 2.17 in Denny
    for i in w_l:
        emis = math.sqrt(c1 / i)  #emissivity a function of the radical of the constants divided by wavelength from equation 2.17 in Denny
        em.append(emis)  #add calculated emissivities to "em" list
    em = np.array(em)  #turn "em" list into "em" array

## 2) Calculate effective temperature from emissivity and mirror temperature
    effective_temp = []  #create list to be filled with effective temperatures
    mirror_temp = float(mirror_temp)  #ensure "mirror_temp" is a float not an integer
    f = interpolate.interp1d(freq, em, bounds_error=False)  #linear interpolation of "em" vs. "freq"
    c2 = const.h / (const.k * mirror_temp)  #a constant from equation 2.20 in Denny
    c3 = const.h / const.k  #a constant from equation 2.20 in Denny
    for i in freq:
        denom = np.exp(c2 * i) - 1  #calculate part of the denominator in equation 2.20 in Denny
        temp_eff = .5 * f(i) * i * c3 / denom  #calculate effective temperature from the product of frequency, corresponding emissivity, constants, and the denominator from equation 2.20 in Denny
            #.5 comes from modes=2
        effective_temp.append(temp_eff)  #add calculated effective temperatures to "effective_temp" list
    temp = np.array(effective_temp)  #turn "effective_temp" list into "temp" array

## 3) Calculate BLING(squared) from effective temperature
    f = interpolate.interp1d(freq, temp, bounds_error=False)  #linear interpolation of "temp" vs. "freq"
    step_size = step_size_k * (np.nanmax(freq) - np.nanmin(freq))  #characterize the level of details wanted from interpolation
        #decreasing "step_size" can lose smoothness of plot and increasing "step_size" lengthens calculation time
    c = 2 * const.h * const.k * step_size  #2 is number of polarization modes, constants come from equation 2.15 in Denny(without the radical) and "step_size" is the increment of the Riemann sum
    int_range = np.zeros((len(freq), 2))  #create 2 by (length of frequency range) array full of 0's to be replaced with values
    int_range_length = freq/2/resol  #2nd term in integration bounds from equation 2.15 in Denny
    int_range[:,0]=freq - int_range_length  #fill up 1st column of 0's array with bottom integration bound from equation 2.15 in Denny
    int_range[:,1]=freq + int_range_length  #fill up 2nd column of 0's array with top integration bound from equation 2.15 in Denny

    ranges = (np.arange(*(list(i)+[step_size])) for i in int_range)  #"i in int_range" refers to each row(which has a start and end to the integration range)
        #for each row, an array is created with values ranging from the starting value to the ending value, in increments of "step_size"

    blingTME_squared = np.array([c*np.sum(i*f(i)) for i in ranges])  #"i in ranges" refers to each row(of the bounds plus "step_size") from the array created above
        #for each row, each of the 2 bounds is multiplied by its corresponding temperature from the linear interpolation done at the start and then are summed
        #summing does the integral for each frequency
        #the sum is multiplied by the number of modes, physical constants, and "step_size" which gives the BLING
        #the result should be square rooted but, since the BLINGs are to be added in quadrature, the squares of each background's BLING are added up then square rooted

    return blingTME_squared


def temp_TME(freq, sigma, mirror_temp, wavelength):  #calculates antenna temperature for "Thermal Mirror Emission"
##    What will be done: 1) Calculate emissivity from surface electrical conductivity("sigma") of specific metal
##                       1) Calculate effective temperature from emissivity and mirror temperature
## 1) Calculate emissivity from surface electrical conductivity("sigma") of specific metal
    em = []  #create list to be filled with emissivities, depending on wavelength
    w_l = wavelength * (1e-6)  #convert wavelength from microns to meters
    c1 = 16 * np.pi * const.c * const.eps0 / sigma  #constants from equation 2.17 in Denny
    for i in w_l:
        emis = (c1 / i)**.5  #emissivity a function of the radical of the constants divided by wavelength from equation 2.17 in Denny
        em.append(emis)  #add calculated emissivities to "em" list
    em = np.array(em)  #turn "em" list into "em" array

## 2) Calculate effective temperature from emissivity and mirror temperature
    effective_temp = []  #create list to be filled with effective temperatures
    mirror_temp = float(mirror_temp)  #ensure "mirror_temp" is a float not an integer
    f = interpolate.interp1d(freq, em, bounds_error=False)  #linear interpolation of "em" vs. "freq"
    c2 = const.h / (const.k * mirror_temp)  #a constant from equation 2.20 in Denny
    c3 = const.h / const.k  #a constant from equation 2.20 in Denny
    for i in freq:
        denom = np.exp(c2 * i) - 1  #calculate part of the denominator in equation 2.20 in Denny
        temp_eff = f(i) * i * c3 / denom  #calculate effective temperature from the product of frequency, corresponding emissivity, constants, and the denominator from equation 2.20 in Denny
            #.5 comes from modes=2
        effective_temp.append(temp_eff)  #add calculated effective temperatures to "effective_temp" list
    temp = np.array(effective_temp)  #turn "effective_temp" list into "temp" array
    return temp


def temp_CMB(freq):  #calculates antenna temperature for "Cosmic Microwave Background"
##    What will be done: 1) Calculate intensity from frequency
##                       2) Calculate antenna temperature from intensity
## 1) Calculate intensity from frequency
    temp = []  #create list to be filled with calculated temperatures
    c1 = const.h / (const.k * cmb_temp)  #constants from equation 2.16 in Denny
    c2 = 2 * const.h / (const.c ** 2)  #constants from equation 2.16 in Denny
    for i in freq:
        denom = np.exp(c1 * i) - 1  #calculate part of the denominator in equation 2.16 in Denny
        intensity = c2 * (i ** 3)/denom  #calculate intensity from equation 2.16 in Denny

## 2) Calculate antenna temperature from intensity
        antenna_temp = intensity * (const.c ** 2)/(const.k * (i**2))  #calculate antenna temperature from equation 2.7 in Denny
            #.5 comes from modes=2
        temp.append(antenna_temp)  #add calculated temperature to "temp" list
    temp = np.array(temp)  #turn "temp" list into "temp" array
    return temp


def temp_AR(freq, rad):  #calculates antenna temperature for "Atmospheric Radiance"
##    What will be done: 1) Interpolate radiance vs. frequency
##                       2) Calculate antenna temperature from radiance
## 1) Interpolate radiance vs. frequency
    rad = rad / (3e6)  #radiance files are given in W/cm^2/st/cm^-1 but are converted to W/m^2/st/Hz
    rad = interpolate.interp1d(freq, rad, bounds_error=False)  #linear interpolation of "rad" vs. "freq"

## 2) Calculate antenna temperature from radiance
    temp = []  #create list to be filled with calculated temperatures
    for i in freq:
        antenna_temp = .5 * rad(i) * (const.c ** 2)/(const.k * (i**2))  #calculate antenna temperature from equation 2.7 in Denny
        temp.append(antenna_temp)  #add calculated temperature to "temp" list
    temp = np.array(temp)  #turn "temp" list into "temp" array
    return temp


def IT(bling_TOT, ratio, ts):  #calculates Integration Time
    return np.array((bling_TOT * ratio / ts)**2, dtype='float')  #follows equation 4.1 in Denny


def TS (freq, inten, trans, mirror_diam, resol):

    # interpolate intensity and transmission
    inten_func = interpolate.interp1d(freq, inten, bounds_error=False)
    trans_func = interpolate.interp1d(freq, trans, bounds_error=False)

    # compute signal falling within each frequency block
    area = np.pi * (0.5 * mirror_diam)**2 # area of mirror collecting the signal

    signal = []
    for freq_i in freq:
        signal.append(area * integrate.quad(
            lambda f: inten_func(f) * trans_func(f),
            freq_i - 0.5 * freq_i / float(resol),
            freq_i + 0.5 * freq_i / float(resol))[0])

    return np.array(signal)
