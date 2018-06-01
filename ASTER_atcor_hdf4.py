import os, sys
import math
import h5py

# sys.path.append(os.path.join(os.getcwd(), 'bin'))
# from interpolated_LUTs import Interpolated_LUTs_Gen as iLUT_gen

# do some things to read the ASTER HDF file 
h5fi = r"C:\tools\py6s_emulator\6S_emulator\examples\AST_L1T_00309132006180645_20150516042027_58950.h5"
f = h5py.File(h5fi)

# sample getting a band
samp_band = f['SWIR']['SWIR_Swath']['Data Fields']['ImageData4']

# check the shapes of valid bands. Need to construct some lists first
data_groups = ['VNIR_Swath', 'SWIR_Swath']
bands_VNIR = ['ImageData1', 'ImageData2', 'ImageData3N']
bands_SWIR = ['ImageData4', 'ImageData5', 'ImageData6', 'ImageData7', 'ImageData8', 'ImageData9']

for group in data_groups:
    if 'VNIR' in group:
        for band in bands_VNIR:
            shp = f['VNIR'][group]['Data Fields'][band].shape
            print("Band {} in {} shape is {}".format(band, group, shp))
            
    else:
        for band in bands_SWIR:
            shp = f['SWIR'][group]['Data Fields'][band].shape
            print("Band {} in {} shape is {}".format(band, group, shp))

            
            
## check it with rasterio
import rasterio
tif_folder = r"C:\tools\py6s_emulator\6S_emulator\examples\output"
tif_base = r"AST_L1T_00309132006180645_20150516042027_58950_"
vnir_tifs = [os.path.join(tif_folder, tif_base + "{}.tif".format(b)) for b in bands_VNIR]
swir_tifs = [os.path.join(tif_folder, tif_base + "{}.tif".format(b)) for b in bands_SWIR]

for f in vnir_tifs:
    with rasterio.open(f, 'r') as src:
        print('vnir: {}\n'.format(src.profile))
        
for f in swir_tifs:
    with rasterio.open(f, 'r') as src:
        print('swir: {}\n'.format(src.profile))
       

## need to get some of the metadata
## relevent fields include: 'TIMEOFDAY', 'PROJECTIONPARAMETERS[1-14]', 'CALENDARDATE', 'POINTINGANGLE.1',
## 'POINTINGANGLE.2', 'POINTINGANGLE.3', 'SOLARDIRECTION': '158.300762, 51.742901'

from osgeo import gdal

# Read in the file and metadata
file_name = r'C:\tools\py6s_emulator\6S_emulator\examples\AST_L1T_00309132006180645_20150516042027_58950.hdf'
aster = gdal.Open(file_name)
aster_sds = aster.GetSubDatasets()
meta = aster.GetMetadata()
aster.Close()
aster = None

## extract the fields (they will be strings)
tod = meta['TIMEOFDAY']
calendar_date = meta['CALENDARDATE']
vnir_view_Z = meta['POINTINGANGLE.1']
swir_view_Z = meta['POINTINGANGLE.2']
solar_d = meta['SOLARDIRECTION'] # 2 elements... azimuth and zenith (i think)
       
'''
# access the LUT
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

# use the LUT for band 1
a, b = iLUT_B1(solar_z,H2O,O3,AOT,alt) # need to incorporate view_z in LUT

elliptical_orbit_correction = 0.03275104*math.cos(doy/59.66638337) + 0.96804905
a *= elliptical_orbit_correction
b *= elliptical_orbit_correction

p = (L-a)/b

print('Surface Reflectance: {}\n'.format(p))
'''