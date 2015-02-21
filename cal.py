import const
import math
import numpy as np
from scipy import integrate, interpolate
from excel import ExcelReader

# These calculations reference equations in 2 papers:
# "Limitations on Observing Submillimeter and Far Infrared Galaxies" by Denny
# and "Fundamental Limits of Detection in the Far Infrared" by Denny et al

# turn a continuous function into a mesh function
def mesh_func (freq, func):
    mesh = []
    for freq_i in freq:
        mesh.append(func(freq_i))
    return np.array(mesh)

# calculate BLING^2 for a list of frequencies and a temperature function
def bling_sq (freq, temp_func, resol, polar_modes=2):
    bsq = []
    for freq_i in freq:
        # bling^2 = 2*h*k_b*int(freq*temp(freq))
        bsq.append(polar_modes * const.h * const.k * integrate.fixed_quad(
            lambda f: f * temp_func(f),
            freq_i - 0.5 * freq_i / float(resol),
            freq_i + 0.5 * freq_i / float(resol))[0])
    return np.array(bsq)

# BLING^2 for CIB, Galactic and Zodiacal Emission
#   temp is a mesh function of discrete points freq
def bling_sub (freq, temp, resol):

    # interpolant of provided mesh function
    temp_func = interpolate.interp1d(freq, temp, bounds_error=False)
    return bling_sq(freq, temp_func, resol, polar_modes=2)

# compute intensity (W/sr*Hz*m^2) from temperature
def intensity (freq, temp):
    intens = []
    for i, temp_i in enumerate(temp):
        intens.append(temp_i * freq[i]**2 * const.k / const.c**2)

    return np.array(intens)

###############################
# Cosmic Microwave Background #
###############################

cmb_T0 = 2.725 # temperature of CMB (in K)

# assume Planck distribution for CMB temperature
#   inten = 2*h*freq^3/c^2 * 1/(exp((h*freq)/(k*T))-1)
#   temp = 1/2 * inten * c^2/(k*freq^2)
#        = h*freq / [k * (exp((h*freq)/(k*T))-1)]
cmb_temp = lambda f: const.h * f / \
    (const.k * (np.exp(const.h * f / (const.k * cmb_T0)) - 1))

# BLING^2 for CMB (assume Planck distribution)
def bling_CMB (freq, resol):
    return bling_sq(freq, cmb_temp, resol, polar_modes=2)

# temperature mesh for CMB
def temp_CMB (freq):
    return mesh_func(freq, cmb_temp)

########################
# Atmospheric Radiance #
########################

# create continuous temperature function
def ar_temp (freq, rad):
    # continuous interpolant function for radiance
    rad = rad / 3e6 # convert from W/cm^2/sr/cm^-1 to W/m^2/st/Hz
    rad_func = interpolate.interp1d(freq, rad, bounds_error=False)

    # calculate temperature at a frequency from radiance
    return lambda f: 0.5 * rad_func(f) * const.c**2 / (const.k * f**2)

# BLING^2 for atmospheric radiance
def bling_AR (freq, rad, resol):
    return bling_sq(freq, ar_temp(freq, rad), resol, polar_modes=1)

# temperature mesh for atmospheric radiance
def temp_AR (freq, rad):
    return mesh_func(freq, ar_temp(freq, rad))


###########################
# Thermal Mirror Emission #
###########################

# create continuous temperature function
def tme_temp (sigma, mirror_temp):
    # compute emissivity
    em_const = 16 * math.pi * const.eps0 / sigma
    em = lambda f: np.sqrt(em_const * f)

    # compute temperature function from emissivity and actual mirror temperature
    # (assume Planck distribution)
    return lambda f: em(f) * const.h * f / \
        (const.k * (np.exp(const.h * f / (const.k * mirror_temp)) - 1))

# BLING^2 for thermal mirror emission
def bling_TME (freq, resol, sigma, mirror_temp):
    return bling_sq(freq, tme_temp(sigma, mirror_temp), resol, polar_modes=2)

# temperature mesh for thermal mirror emission
def temp_TME(freq, sigma, mirror_temp):
    return mesh_func(freq, tme_temp(sigma, mirror_temp))

###


# integration time needed
def IT (bling_TOT, snr, ts):
    # snr = signal / noise
    #     = (signal_0 / bling) * sqrt(time)
    # time = (bling * snr / signal)^2
    return (bling_TOT * snr / ts)**2

# total signal
def TS (freq, inten, trans, mirror_diam, resol):

    # interpolate intensity and transmission
    inten_func = interpolate.interp1d(freq, inten, bounds_error=False)
    trans_func = interpolate.interp1d(freq, trans, bounds_error=False)

    # compute signal falling within each frequency block
    area = math.pi * (0.5 * mirror_diam)**2 # area of mirror collecting the signal

    signal = []
    for freq_i in freq:
        signal.append(area * integrate.fixed_quad(
            lambda f: inten_func(f) * trans_func(f),
            freq_i - 0.5 * freq_i / float(resol),
            freq_i + 0.5 * freq_i / float(resol))[0])

    return signal
