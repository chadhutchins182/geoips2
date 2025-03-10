# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
# # # 
# # # Author:
# # # Naval Research Laboratory, Marine Meteorology Division
# # # 
# # # This program is free software: you can redistribute it and/or modify it under
# # # the terms of the NRLMMD License included with this program.  If you did not
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
# # # information.
# # # 
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # # included license for more details.

''' This EWS-G(Electro-Optical Infrared Weather System - Geostationary) reader is designed for reading the
    EWS-G data files (EWS-G is renamed from GOES-13).  The reader is only using the python functions and 
    xarray variables.  The reader is based on EWS-G data in netcdf4 format.

    V1.0:  NRL-Monterey, 02/25/2021

    ***************  EWS-G file information  ****************************
   Example of the gvar filename:   2020.1212.0012.goes-13.gvar.nc

   Note:
            channel-3 is not available for EWS-G.
            gvar_Ch3(TIR=5.8-7.3um, ctr=6.48um,4km): unit=temp-deg(C), scale_factor=0.01 

   variables: 
            gvar_Ch1(VIS=0.55-0.75um, ctr=0.65um,1km): unit=albedo*100,  scale_factor=0.01
            gvar_Ch2(MWIR=3.8-4.0um,  ctr=3.9um, 4km): unit=temp-deg(C), scale_factor=0.01
            gvar_Ch4(TIR=10.2-11.2um, ctr=10.7um,4km): unit=temp-deg(C), scale_factor=0.01 
            gvar_Ch6(TIR=12.9-13.7um, ctr=13.3um 4km): unit=temp-deg(C), scale_factor=0.01
            latitude: unit=degree
            longitude:unit=degree
            sat_zenith: unit=degree
            sun_zenith: unit=degree
            rel_azimuth:unit=degree

            variable array definition:  var(scan,pix); scan-->lines, pix-->samples

   attributes: many 

'''

# Python Standard Libraries
import logging
import os

# Installed Libraries
import numpy as np
import xarray as xr
import calendar
import pandas as pd


# If this reader is not installed on the system, don't fail altogether, just skip this import. This reader will
# not work if the import fails, and the package will have to be installed to process data of this type.

try: 
    import netCDF4 as ncdf
except: 
    print('Failed import netCDF4. If you need it, install it.')


#@staticmethod                                     # not sure where it is uwas used?

LOG = logging.getLogger(__name__)

# gvar_ch6 has only half scanlines of other channels (1,2,4),we temporally do not read the ch6 in.
#   we will modify this reader if gvar_ch6 is needed in the future.  
VARLIST = ['gvar_ch1','gvar_ch2','gvar_ch4',
           'latitude','longitude','sun_zenith','sat_zenith','rel_azimuth']

# setup needed to convert var_name used in geoips2: i.e., SunZenith (not sun_zenith) is used. 
xvarnames = {'sun_zenith': 'SunZenith',
             'sat_zenith': 'SatZenith',
             'rel_azimuth': 'SatAzimuth'}

reader_type = 'standard'


def ewsg_netcdf(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):

    ''' Read EWS-G data in netcdf4 format.

    All GeoIPS 2.0 readers read data into xarray Datasets - a separate
    dataset for each shape/resolution of data - and contain standard metadata information.

    Args:
        fnames (list): List of strings, full paths to files
        metadata_only (Optional[bool]):
            * DEFAULT False
            * return before actually reading data if True
        chans (Optional[list of str]):
            * NOT YET IMPLEMENTED
                * DEFAULT None (include all channels)
                * List of desired channels (skip unneeded variables as needed)
        area_def (Optional[pyresample.AreaDefinition]):
            * NOT YET IMPLEMENTED
                * DEFAULT None (read all data)
                * Specify region to read
        self_register (Optional[str]):
            * NOT YET IMPLEMENTED
                * DEFAULT False (read multiple resolutions of data)
                * register all data to the specified resolution.

    Returns:
        dict of xarray.Datasets: dict of xarray.Dataset objects with required
            Variables and Attributes: (See geoips2/docs :doc:`xarray_standards`),
            dict key can be any descriptive dataset id
   '''


    #from IPython import embed as shell
    from datetime import datetime
    import pandas as pd

   
    # --------------- loop input files ---------------
    xarray_ewsg = xr.Dataset()
    xarray_ewsg.attrs['original_source_filenames'] = []
    #LOG.info('Requested Channels: %s', chans)

    for fname in fnames:

        # check for a correct goes-13 data file

        data_name=os.path.basename(fname).split('_')[-1].split('.')[-1]

        if data_name != 'nc':
            print('Warning: EWS-G data type:  data_type=', data_name)
            raise

        # open the paired input files
        ncdf_file = ncdf.Dataset(str(fname), 'r')
        LOG.info('    Trying file %s', fname)

        if ncdf_file.satellite == 'goes-13':
            print('found a NOAA EWS-G data file')
        else:
            print('not a NOAA EWS-G data file: skip it')
            raise
   
        # *************** input VIRRS variables  and output xarray required by geoips2 *****************
        
        #for varname in ncdf_file.variables.keys():
        for var in VARLIST:
            varname=var
            data=ncdf_file[varname]
            #masked_data=np.ma.masked_equal(ncdf_file[varname],ncdf_file[varname].missing_value)
            masked_data=np.ma.masked_equal(data,data.missing_value)

            if var in xvarnames:
                varname = xvarnames[var]             #rename zenith/azimuth-related variables

            xarray_ewsg[varname]=xr.DataArray(masked_data)     
            '''
            # scale_factor should not be applied
            if 'scale_factor' in data.ncattrs():
                # apply scale_factor correction 
                #xarray_ewsg[varname]=xarray_ewsg[varname]*ncdf_file[varname].scale_factor
                xarray_ewsg[varname]=xarray_ewsg[varname]*data.scale_factor
            '''
            #convert unit from degree to Kelvin for ch2, ch4, and ch6 (ch1 is in unit of albedo)
            if varname in ['gvar_ch2','gvar_ch4', 'gvar_ch6']:   
                xarray_ewsg[varname]=xarray_ewsg[varname]+273.15
                xarray_ewsg[varname].attrs['units']='Kelvin'          

        # setup attributes
        # use fname to get an initial info of  year, month, day
        # test hour/minute/second of "start_datetime" info from start_time (second of the day)
        # add scan_time info to determine the "end_datetime". scan_time has time of scans for 
        #     this input data file(one obs).  If end_time of this data >24 hr, modify value of "day"
        #     from fname.  Note: scan_time units are seconds from (start_time + time_adjust)  

        # date info from fname
        #        1  2  3  4  5  6  7  8  9  10 11 12
        days_mo   =[31,28,31,30,31,30,31,31,30,31,30,31]
        days_mo_lp=[31,29,31,30,31,30,31,31,30,31,30,31]     #Leap year
                
        # date information is not contained in the data so we have to get it from filename
        data_name=os.path.basename(fname)  
        yr=int(data_name.split('.')[0])   
        mo=int(data_name.split('.')[1][0:2])   
        dy=int(data_name.split('.')[1][2:4])
        hr=int(data_name.split('.')[2][0:2])
        mm=int(data_name.split('.')[2][2:4])
        
        # determine a Leap Year?
        if calendar.isleap(yr):
            days=days_mo_lp[mo-1]
        else:
            days=days_mo[mo-1]
        
        # second of the date for this file
        start_time=ncdf_file.start_time+ncdf_file.time_adjust + ncdf_file.scan_time[0]
        end_time=ncdf_file.start_time+ncdf_file.time_adjust + ncdf_file.scan_time[29]

        yr_s=yr
        yr_e=yr
        mo_s=mo
        mo_e=mo
        dy_s=dy
        dy_e=dy        
        hr_s=int(start_time/3600)
        mm_s=int((start_time- hr_s*3600)/60)
        ss_s=int(start_time - (hr_s*3600+mm_s*60))
        hr_e=int(end_time/3600)
        mm_e=int((end_time- hr_e*3600)/60)
        ss_e=int(end_time - (hr_e*3600+mm_e*60))

        if hr_s >= 24:
            dy_s_=dy+1         #forward to the next date
            hr_s=hr_s-24
            if dy_s >days:     #move to next mon
                mo_s=mo+1
                if mo_s >12:   #move to near year
                    yr_s=yr+1  
        if hr_e >= 24: 
            dy_e_=dy+1         #forward to the next date
            hr_e=hr_e-24
            if dy_e >days:     #move to next mon
                mo_e=mo+1
                if mo_e >12:   #move to near year
                    yr_e=yr+1  
           
        start_scan='%04d%02d%02d%02d%02d%02d' % (yr_s,mo_s,dy_s,hr_s,mm_s,ss_s)  
        end_scan='%04d%02d%02d%02d%02d%02d' % (yr_e,mo_e,dy_e,hr_e,mm_e,ss_e)  
    
        # convert date in required format
        Start_date= pd.to_datetime(start_scan,format='%Y%m%d%H%M%S')
        End_date= pd.to_datetime(end_scan,format='%Y%m%d%H%M%S')

        xarray_ewsg.attrs['start_datetime'] = Start_date
        xarray_ewsg.attrs['end_datetime']   = End_date
        xarray_ewsg.attrs['source_name']    = 'gvissr'       #ncdf_file.sensor_name
        if ncdf_file.satellite == 'goes-13':
            xarray_ewsg.attrs['platform_name']  = 'ews-g'
        xarray_ewsg.attrs['data_provider']  = 'noaa'
        xarray_ewsg.attrs['original_source_filenames'] += [os.path.basename(fname)]
        
        # MTIFs need to be "prettier" for PMW products, so 2km resolution for final image
        xarray_ewsg.attrs['sample_distance_km'] = 2
        xarray_ewsg.attrs['interpolation_radius_of_influence'] = 3000

        # close the files
        ncdf_file.close()

    return {'LOW': xarray_ewsg,
            'METADATA': xarray_ewsg[[]]}
