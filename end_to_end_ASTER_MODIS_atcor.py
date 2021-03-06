import os, sys
# import urllib2 # use this for python 2x
import urllib.request as urllib2
import subprocess
from osgeo import gdal
import datetime
# import HTMLParser
import re
import lxml.html
from io import BytesIO
from lxml import etree
import numpy as np
import math

sys.path.append(r'C:\tools\py6s_emulator\6S_emulator\bin')
from interpolated_LUTs import Interpolated_LUTs_Gen as iLUT_gen

def retrieveMODISlistings(url):

    tree = etree.HTML(urllib2.urlopen(url_base).read())

    # data = urllib2.urlopen(url_base).read()
    # dom = lxml.html.parse(BytesIO(data))
    # xpatheval=etree.XPathDocumentEvaluator(dom)
    # xpatheval('//*[@id="ftp-directory-list"]/tbody/tr[2]/td[1]/a')
    
    # the xpath argument retrieved from F12 mode in chrome
    table = tree.xpath('//*[@id="ftp-directory-list"]')[0]
    
    # grab the hdf files (tested and probably only works for the MODIS site.)
    hdf_files = [row[0][0].items()[0][1] for row in table[2:]]
        
    return hdf_files
    
def sortByTOD(flist, timeofday, num=1):

    hourmin = int(timeofday[:4])    
    times = [int(f.split('/')[-1].split('.')[2]) for f in flist]
    
    times_arr = np.abs(np.array(times) - hourmin)
    inds = list(np.argsort(times_arr))
    
    sorted = [flist[i] for i in inds]
    
    return sorted[:num]
    
    

def modisInfoFromAster(file_name):

    aster = gdal.Open(file_name)
    aster_sds = aster.GetSubDatasets()
    meta = aster.GetMetadata()
    # aster.Close()
    # aster = None

    ## extract the fields (they will be strings)
    tod = meta['TIMEOFDAY']
    calendar_date = meta['CALENDARDATE']
    vnir_view_Z = meta['POINTINGANGLE.1']
    swir_view_Z = meta['POINTINGANGLE.2']
    solar_d = meta['SOLARDIRECTION'] # 2 elements... azimuth and zenith (i think)
    
    return calendar_date, tod
    
def viewInfoFromAster(file_name):

    aster = gdal.Open(file_name)
    meta = aster.GetMetadata()
    # aster.Close()
    # aster = None

    ## extract the fields (they will be strings)
    tod = meta['TIMEOFDAY']
    calendar_date = meta['CALENDARDATE']
    vnir_view_Z = meta['POINTINGANGLE.1']
    swir_view_Z = meta['POINTINGANGLE.2']
    solar_d = meta['SOLARDIRECTION'] # 2 elements... azimuth and zenith (i think)
    
    solar_d = [float(s) for s in solar_d.split(',')]
    vnir_view_Z = float(vnir_view_Z)
    swir_view_Z = float(swir_view_Z)    
    
    return vnir_view_Z, swir_view_Z, solar_d

def bboxInfoFromAster(file_name):

    aster = gdal.Open(file_name)
    meta = aster.GetMetadata()
    # aster.Close()
    # aster = None

    ## extract the fields (they will be strings)
    n = float(meta['NORTHBOUNDINGCOORDINATE'])
    s = float(meta['SOUTHBOUNDINGCOORDINATE'])
    e = float(meta['EASTBOUNDINGCOORDINATE'])
    w = float(meta['WESTBOUNDINGCOORDINATE'])    
    
    return n,s,e,w

def summarizeMODIS_mod04(hdf, aster_bbox):

    mod = gdal.Open(hdf)
    mod_sds = mod.GetSubDatasets()
    
    for sd in mod_sds:
    
        if 'Longitude' in sd[1]:
            longitude_sd = sd[0]
        
        if 'Latitude' in sd[1]:
            latitude_sd = sd[0]
        
        if 'Deep_Blue_Aerosol_Optical_Depth_550_Land' == sd[0].split(':')[-1]:
            aod_sd = sd[0]
            
    # 'close' the file
    mod = None
    
    ## should now have the file paths to open these arrays and sample within the aster_bbox
    lon_arr = gdal.Open(longitude_sd).ReadAsArray()
    lat_arr = gdal.Open(latitude_sd).ReadAsArray()
    aod_arr = gdal.Open(aod_sd).ReadAsArray()
    
    # get the scale and offset
    scale_factor_aod = float(gdal.Open(aod_sd).GetMetadata()['scale_factor'])
    add_offset_aod = float(gdal.Open(aod_sd).GetMetadata()['add_offset'])
    
    print(scale_factor_aod, add_offset_aod)
    
    # create the logical array for the AOI
    lat_max, lat_min, lon_min, lon_max = aster_bbox
    sample_arr = np.where((lon_arr > lon_min) & (lon_arr < lon_max) & (lat_arr > lat_min) & (lat_arr < lat_max))[0]
    
    # sample the data
    temp_arr = aod_arr[sample_arr]
    temp_arr = (temp_arr[temp_arr > -9999] - add_offset_aod) * scale_factor_aod
    aod_mean = np.mean(temp_arr)
            
    return temp_arr, aod_mean
    
    
def summarizeMODIS_mod05(hdf, aster_bbox):

    mod = gdal.Open(hdf)
    mod_sds = mod.GetSubDatasets()
    
    for sd in mod_sds:
    
        if 'Longitude' in sd[1]:
            longitude_sd = sd[0]
        
        if 'Latitude' in sd[1]:
            latitude_sd = sd[0]
        
        # use the Water_Vapor_Near_Infrared dataset to avoid problems (known issue)
        if 'Water_Vapor_Near_Infrared' == sd[0].split(':')[-1]:
            wv_sd = sd[0]
            
    # 'close' the file
    mod = None
    
    ## should now have the file paths to open these arrays and sample within the aster_bbox
    lon_arr = gdal.Open(longitude_sd).ReadAsArray()
    lat_arr = gdal.Open(latitude_sd).ReadAsArray()
    wv_arr = gdal.Open(wv_sd).ReadAsArray()
    
    # get the scale and offset
    scale_factor_wv = float(gdal.Open(wv_sd).GetMetadata()['scale_factor'])
    add_offset_wv = float(gdal.Open(wv_sd).GetMetadata()['add_offset'])
    
    print(scale_factor_wv, add_offset_wv)
    
    # create the logical array for the AOI
    lat_max, lat_min, lon_min, lon_max = aster_bbox
    sample_arr = np.where((lon_arr > lon_min) & (lon_arr < lon_max) & (lat_arr > lat_min) & (lat_arr < lat_max))[0]
    
    # sample the data
    temp_arr = wv_arr[sample_arr]
    temp_arr = (temp_arr[temp_arr > -9999] - add_offset_wv) * scale_factor_wv
    wv_mean = np.mean(temp_arr)
            
    return temp_arr, wv_mean
    
    
def summarizeMODIS_mod07(hdf, aster_bbox):

    mod = gdal.Open(hdf)
    mod_sds = mod.GetSubDatasets()
    
    for sd in mod_sds:
    
        if 'Longitude' in sd[1]:
            longitude_sd = sd[0]
        
        if 'Latitude' in sd[1]:
            latitude_sd = sd[0]
        
        if 'Total_Ozone' == sd[0].split(':')[-1]:
            oz_sd = sd[0]
            
        if 'Water_Vapor' == sd[0].split(':')[-1]:
            wv_sd = sd[0]
            
    # 'close' the file
    mod = None
    
    ## should now have the file paths to open these arrays and sample within the aster_bbox
    lon_arr = gdal.Open(longitude_sd).ReadAsArray()
    lat_arr = gdal.Open(latitude_sd).ReadAsArray()
    oz_arr = gdal.Open(oz_sd).ReadAsArray()
    wv_arr = gdal.Open(wv_sd).ReadAsArray()
    
    # get the scale and offset
    scale_factor_oz = float(gdal.Open(oz_sd).GetMetadata()['scale_factor'])
    add_offset_oz = float(gdal.Open(oz_sd).GetMetadata()['add_offset'])
    
    scale_factor_wv = float(gdal.Open(wv_sd).GetMetadata()['scale_factor'])
    add_offset_wv = float(gdal.Open(wv_sd).GetMetadata()['add_offset'])
    
    print(scale_factor_oz, add_offset_oz, scale_factor_wv, add_offset_wv)
    
    # get the logical array for the AOI
    lat_max, lat_min, lon_min, lon_max = aster_bbox
    sample_arr = np.where((lon_arr > lon_min) & (lon_arr < lon_max) & (lat_arr > lat_min) & (lat_arr < lat_max))[0]
    
    # sample the values
    temp_arr_oz = oz_arr[sample_arr]
    temp_arr_oz = (temp_arr_oz[temp_arr_oz > -9999] - add_offset_oz) * scale_factor_oz
    
    temp_arr_wv = wv_arr[sample_arr]
    temp_arr_wv = (temp_arr_wv[temp_arr_wv > -9999] - add_offset_wv) * scale_factor_wv
    
    oz_mean = np.mean(temp_arr_oz)
    wv_mean = np.mean(temp_arr_wv)
            
    return temp_arr_oz, temp_arr_wv, oz_mean, wv_mean
        
    
def toJulianDay(datestr):

    return 

    


# change directory to correct path
dl_dir = r"C:\tools\py6s_emulator\6S_emulator\examples"
save_dir = r'C:\tools\py6s_emulator\6S_emulator\examples\download' # make parameter
os.chdir(dl_dir)

#################################################################################################################
### ASTER METADATA PROCESSING ###
#################################################################################################################

# specify the ASTER file (potentially download some other way... for now, requested through EarthData) 
# make parameter
aster_file = r'C:\tools\py6s_emulator\6S_emulator\examples\AST_L1T_00309132006180645_20150516042027_58950.hdf'

# get the bounding box
n,s,e,w = bboxInfoFromAster(aster_file)
aster_bbox = [n,s,w,e]

# get the calendar_Date
calendar_date, tod = modisInfoFromAster(aster_file)

# convert the calendar_date to year / month / day
year  = int(calendar_date[0:4])
month = int(calendar_date[4:6])
day   = int(calendar_date[6:])

# convert calendar date to doy
d = datetime.date(year, month, day)
doy = d.timetuple().tm_yday

#################################################################################################################
#################################################################################################################
#################################################################################################################


# info for downloading modis data
# example file https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/
#                       MOD05_L2/2006/066/MOD05_L2.A2006066.0000.061.2017263153530.hdf
aerosol_prod = 'MOD04_L2'
total_precip = 'MOD05_L2'
atm_profile  = 'MOD07_L2'

# download the necessary files
for prod in (aerosol_prod, total_precip, atm_profile):

    print('downloading {} for year {} day {}'.format(prod, year, doy))

    # construct the MODIS url path for the product name
    # prod = aerosol_prod
    url_base = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/{}/{}/{}/'.format(prod, year, doy)

    # get the MODIS HDF files
    potential_files = retrieveMODISlistings(url_base)

    # find the ones that are closest to the time of day
    closest_MODIS = sortByTOD(potential_files, tod, 5)

    # download the modis data (TODO)

    # url2 = r'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD07_L2/2006/010/MOD07_L2.A2006010.0100.061.2017261010810.hdf'
    hdf_file = os.path.basename(closest_MODIS[0])
    url = url_base + hdf_file
    full_fname = os.path.join(save_dir, hdf_file)
    # fname = os.path.basename(url)
    
    if not os.path.exists(full_fname):
        filedata = urllib2.urlopen(url)
        datatowrite=filedata.read()
        with open(full_fname, 'wb') as f:
            f.write(datatowrite)
        
    # convert the file to hdf5
    # print('converting to hdf5')
    # h5_file = full_fname.replace('.hdf', '.h5')
    # subprocess.call([h4_to_h5_exe, full_fname, full_fname.replace('.hdf', '.h5')])
    
    
    ## read the MODIS products and summarize over the ASTER scene
    # extract the MODIS data with the ASTER scene extents
    if prod == aerosol_prod:
        aod_arr, aod_mean_val = summarizeMODIS_mod04(full_fname, aster_bbox)        
        
    if prod == total_precip:
        wv_arr, wv_mean_val = summarizeMODIS_mod05(full_fname, aster_bbox)
        
    if prod == atm_profile:
        ozone_arr, wv_arr2, ozone_mean_val, wv_mean_val_2 = summarizeMODIS_mod07(full_fname, aster_bbox)


# look at the differences in mod05 and mod07 water vapor distributions
from matplotlib import pyplot as plt

show = False
if show:
    plt.hist(wv_arr.flatten(), bins=100, label='mod05')
    plt.hist(wv_arr2.flatten(), bins=100, label='mod07', alpha = 1.)
    plt.legend()
    plt.show()

##################################################################
##################################################################
#############  apply 6S correction to input image ################
##################################################################
##################################################################

# import the function to convert the ASTER L1T DNs to surface leaving radiance
from ASTERL1T_proc import asterDN2RAD 

# set some band lists
bands_VNIR = ['ImageData1', 'ImageData2', 'ImageData3N']
bands_SWIR = ['ImageData4', 'ImageData5', 'ImageData6', 'ImageData7', 'ImageData8', 'ImageData9']

# convert to surface leaving radiance
rad_arr_0 = asterDN2RAD(aster_file, bands_VNIR[0])
rad_arr_1 = asterDN2RAD(aster_file, bands_VNIR[1])
rad_arr_2 = asterDN2RAD(aster_file, bands_VNIR[2])

## process in 6S emulator with ASTER LUT
# access the LUT
iLUT_path = r'C:\tools\py6s_emulator\6S_emulator\files\LUTs\ASTER\Continental\view_zenith_0\files\iLUTs\ASTER\Continental\view_zenith_0'
iLUTs = iLUT_gen('ASTER', iLUT_path)
iLUTs_all_wavebands = iLUTs.get()

# get the view info re:ASTER
vnir_view, _, sol_view = viewInfoFromAster(aster_file)

# set some 6S parameters
alt = 0.5280               # target altitude (km) example for Denver area??
solar_z = sol_view[1]      # solar zenith angle (degrees)
view_z = vnir_view         # view zenith angle (degrees)
H2O = wv_mean_val          # water vapour (g cm-2)
O3 = ozone_mean_val*0.001  # ozone (atm-cm) (convert from Dobson Unit (DU) to atm-cm using 0.001 CF)
AOT = aod_mean_val         # aerosol optical thickness

# interpolate with the LUT
# need to incorporate view_z in LUT... currently assuming nadir
a, b = iLUT_B1(solar_z, H2O, O3, AOT, alt) 
elliptical_orbit_correction = 0.03275104*math.cos(doy/59.66638337) + 0.96804905
a *= elliptical_orbit_correction
b *= elliptical_orbit_correction

# apply the correction to non-masked pixels
p0 = (rad_arr_0 - a)/b 
p0[rad_arr_0 == 0] = 0

p1 = (rad_arr_1 - a)/b 
p1[rad_arr_1 == 0] = 0

p2 = (rad_arr_2 - a)/b 
p2[rad_arr_2 == 0] = 0

show = True
if show:
    fig, ax = plt.subplots(ncols = 2, nrows = 3 , figsize=(10,10))
    ax[0,0].imshow(rad_arr_0)
    ax[0,0].set_title('blue band radiance')
    
    ax[0,1].imshow(p0)
    ax[0,1].set_title('blue band reflectance')
    
    ax[1,0].imshow(rad_arr_0)
    ax[1,0].set_title('green band radiance')
    
    ax[1,1].imshow(p0)
    ax[1,1].set_title('green band reflectance')
    
    ax[2,0].imshow(rad_arr_0)
    ax[2,0].set_title('red band radiance')
    
    ax[2,1].imshow(p0)
    ax[2,1].set_title('red band reflectance')
    
    plt.show()



