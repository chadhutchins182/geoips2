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

'''Read derived surface winds from SAR, SMAP, SMOS, and AMSR netcdf data.'''
import logging
from os.path import basename
LOG = logging.getLogger(__name__)

MS_TO_KTS = 1.94384
DEG_TO_KM = 111.321

reader_type = 'standard'


def read_knmi_data(wind_xarray):
    ''' Reformat ascat xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts, wind_dir_deg_met
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    # Setting standard geoips attributes
    LOG.info('Reading %s data', wind_xarray.source)
    if wind_xarray.source == 'MetOp-C ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metop-c'
    elif wind_xarray.source == 'MetOp-B ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metop-b'
    elif wind_xarray.source == 'MetOp-A ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metop-a'
    elif wind_xarray.source == 'ScatSat-1 OSCAT':
        wind_xarray.attrs['source_name'] = 'oscat'
        wind_xarray.attrs['platform_name'] = 'scatsat-1'
        
    # Pixel size stored as "25.0 km"
    pixel_size = float(wind_xarray.pixel_size_on_horizontal.replace(' km', ''))

    # Interpolation Radius of Influence 
    wind_xarray.attrs['interpolation_radius_of_influence'] = pixel_size * 1000.0

    wind_xarray.attrs['sample_distance_km'] = pixel_size

    # setting wind_speed_kts appropriately
    wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'] * MS_TO_KTS
    wind_xarray['wind_speed_kts'].attrs = wind_xarray['wind_speed'].attrs
    wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'

    # Directions in netcdf file use oceanography conventions
    wind_xarray['wind_dir_deg_met'] = wind_xarray['wind_dir'] - 180
    wind_xarray['wind_dir_deg_met'].attrs = wind_xarray['wind_dir'].attrs
    wind_xarray['wind_dir_deg_met'] = wind_xarray['wind_dir_deg_met'].where(wind_xarray['wind_dir_deg_met'] >= 0,
                                                                            wind_xarray['wind_dir_deg_met'] + 360)
    wind_xarray.wind_dir_deg_met.attrs['standard_name'] = 'wind_from_direction'
    wind_xarray.wind_dir_deg_met.attrs['valid_max'] = 360

    # Set lat/lons/timestamp appropriately
    wind_xarray = wind_xarray.rename({'lat': 'latitude', 'lon': 'longitude', 'time': 'timestamp'})
    import xarray
    import numpy
    RAIN_FLAG_BIT = 9
    wind_xarray['rain_flag'] = xarray.ufuncs.logical_and(wind_xarray['wvc_quality_flag'], (1 << RAIN_FLAG_BIT))
                                     
    wind_xarray = wind_xarray.set_coords(['timestamp'])
    return {'WINDSPEED': wind_xarray}


def scat_knmi_winds_netcdf(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):
    ''' Read one of SAR, SMAP, SMOS, AMSR derived winds from netcdf data.

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
        list of xarray.Datasets: list of xarray.Dataset objects with required
            Variables and Attributes: (See geoips2/docs :doc:`xarray_standards`)
    '''

    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp, get_max_from_xarray_timestamp
    import xarray
    # Only SAR reads multiple files
    fname = fnames[0]
    wind_xarray = xarray.open_dataset(str(fname))

    wind_xarray.attrs['source_name'] = 'unknown'
    wind_xarray.attrs['platform_name'] = 'unknown'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 'unknown'
    wind_xarray.attrs['sample_distance_km'] = 'unknown'

    wind_xarray.attrs['data_provider'] = 'knmi'
    wind_xarray.attrs['original_source_filenames'] = [basename(fname)]
    wind_xarray.attrs['minimum_coverage'] = 20

    LOG.info('Read data from %s', fname)

    if hasattr(wind_xarray, 'title_short_name') and 'ASCAT' in wind_xarray.title_short_name:
        wind_xarrays = read_knmi_data(wind_xarray)

    if hasattr(wind_xarray, 'title_short_name') and 'OSCAT' in wind_xarray.title_short_name:
        wind_xarrays = read_knmi_data(wind_xarray)

    for wind_xarray in wind_xarrays.values():

        LOG.info('Setting standard metadata')
        wind_xarray.attrs['start_datetime'] = get_min_from_xarray_timestamp(wind_xarray, 'timestamp')
        wind_xarray.attrs['end_datetime'] = get_max_from_xarray_timestamp(wind_xarray, 'timestamp')

        if 'wind_speed_kts' in wind_xarray.variables:
            # These text files store wind speeds natively in kts
            wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'

        LOG.info('Read data %s start_dt %s source %s platform %s data_provider %s roi %s native resolution',
                 wind_xarray.attrs['start_datetime'],
                 wind_xarray.attrs['source_name'],
                 wind_xarray.attrs['platform_name'],
                 wind_xarray.attrs['data_provider'],
                 wind_xarray.attrs['interpolation_radius_of_influence'],
                 wind_xarray.attrs['sample_distance_km'])

    wind_xarrays['METADATA'] = wind_xarray[[]]

    return wind_xarrays
