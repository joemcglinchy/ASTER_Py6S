import os, sys

sys.path.append(os.path.join(os.getcwd(), 'bin'))
from interpolated_LUTs import Interpolated_LUTs_Gen as iLUT_gen


iLUT_path = r'C:\tools\py6s_emulator\6S_emulator\files\LUTs\ASTER\Continental\view_zenith_0\files\iLUTs\ASTER\Continental\view_zenith_0'
iLUTs = iLUT_gen('ASTER', iLUT_path)
iLUTs_all_wavebands = iLUTs.get()

alt = 0      # target altitude (km)
solar_z = 20 # solar zenith angle (degrees)
view_z = 0   # view zentith angle (degrees)
doy = 4      # Earth-Sun distance (Astronomical Units)

H2O = 1    # water vapour (g cm-2)
O3 = 0.4   # ozone (atm-cm)
AOT = 0.3  # aerosol optical thickness

L=120 # at sensor radiance

import math

elliptical_orbit_correction = 0.03275104*math.cos(doy/59.66638337) + 0.96804905
a *= elliptical_orbit_correction
b *= elliptical_orbit_correction

p = (L-a)/b

print('Surface Reflectance: {}\n'.format(p))