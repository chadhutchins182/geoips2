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


def read_smos_data(wind_xarray, fname):
    ''' Reformat SMOS xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    import xarray
    import numpy
    from datetime import datetime, timedelta
    LOG.info('Reading SMOS data')

    # Attributes aren't set in the data files - use the file names to determine the version
    # 0 is good, 1 is fair, 2 is poor
    if '_110_' in fname:
        # Eliminate "poor" retrievals in the "old" version
        wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'].where(wind_xarray['quality_level'] < 2)[0, :, :]
    elif '_300_' in fname:
        # 2 eliminates everything anywhere close to land, so keep everything.
        wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'].where(wind_xarray['quality_level'] < 3)[0, :, :]
    else:
        # Default to keeping everything, in case filenames change
        wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'].where(wind_xarray['quality_level'] < 3)[0, :, :]
    wind_xarray['wind_speed_kts'] = xarray.DataArray(data=numpy.flipud(wind_xarray.wind_speed_kts) * MS_TO_KTS,
                                                     name='wind_speed_kts',
                                                     coords=wind_xarray['wind_speed_kts'].coords)

    # Set lat/lons appropriately
    # These are (1440x720)
    lats2d, lons2d = numpy.meshgrid(wind_xarray.lat, wind_xarray.lon)
    # Full dataset is 720x1440x2
    wind_xarray['latitude'] = xarray.DataArray(data=numpy.flipud(lats2d.transpose()),
                                               name='latitude',
                                               coords=wind_xarray['wind_speed_kts'].coords)
    wind_xarray['longitude'] = xarray.DataArray(data=lons2d.transpose(),
                                                name='longitude',
                                                coords=wind_xarray['wind_speed_kts'].coords)
    wind_xarray = wind_xarray.set_coords(['latitude', 'longitude'])
    # timearray = numpy.zeros(wind_xarray.wind_speed_kts.shape).astype(int) + wind_xarray.time.values[0]

    timearray = numpy.ma.masked_array(data=numpy.zeros(wind_xarray.wind_speed_kts.shape).astype(int)
                                      + wind_xarray.time.values[0],
                                      mask=True)
    from numpy import datetime64, timedelta64
    from netCDF4 import Dataset
    ncobj = Dataset(fname)
    basedt = datetime64(datetime.strptime('19900101', '%Y%m%d'))
    nctimearray = numpy.flipud(ncobj.variables['measurement_time'][...][0, :, :])
    timeinds = numpy.ma.where(nctimearray)
    # Check if there are any unmasked timeinds, if so update timearray
    if numpy.size(timeinds) > 0:
        timedata = nctimearray[timeinds].data.tolist()
        timevals = numpy.ma.masked_array([basedt + timedelta64(timedelta(days=xx)) for xx in timedata])
        timearray[timeinds] = timevals
    # Otherwise set timearray as unmasked values
    else:
        timearray = timearray.data
    wind_xarray['timestamp'] = xarray.DataArray(data=timearray,
                                                name='timestamp',
                                                coords=wind_xarray['wind_speed_kts'].coords)
    return {'WINDSPEED': wind_xarray}


def smos_winds_netcdf(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):
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
    import numpy
    import xarray
    # Only SAR reads multiple files
    fname = fnames[0]
    wind_xarray = xarray.open_dataset(str(fname))
    # Set attributes appropriately
    wind_xarray.attrs['original_source_filenames'] = [basename(fname)]
    wind_xarray.attrs['minimum_coverage'] = 20
    wind_xarray.attrs['source_name'] = 'smos-spd'
    wind_xarray.attrs['platform_name'] = 'smos'
    wind_xarray.attrs['data_provider'] = 'esa'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 25000
    # wind_xarray.attrs['sample_distance_km'] = DEG_TO_KM / 4
    wind_xarray.attrs['sample_distance_km'] = 25.0

    # Checking if the wind_xarray.time is valid
    if not isinstance(wind_xarray.time.values[0], numpy.datetime64) and wind_xarray.time.values[0].year > 3000:
        from datetime import datetime, timedelta
        cov_start = datetime.strptime(wind_xarray.time_coverage_start, '%Y-%m-%dT%H:%M:%S Z')
        cov_end = datetime.strptime(wind_xarray.time_coverage_end, '%Y-%m-%dT%H:%M:%S Z')
        time = cov_start + timedelta(seconds=(cov_end - cov_start).total_seconds()/2)
        time_attrs = wind_xarray.time.attrs
        wind_xarray['time'] = numpy.array([time],dtype=numpy.datetime64)
        wind_xarray['time'].attrs = time_attrs

    LOG.info('Read data from %s', fname)

    # SMOS timestamp is not read in correctly natively with xarray - must pass fname so we can get time
    # information directly from netCDF4.Dataset open
    wind_xarrays = read_smos_data(wind_xarray, fname)

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
    if wind_xarrays['METADATA'].start_datetime == wind_xarrays['METADATA'].end_datetime:
        # Use alternate attributes to set start and end datetime
        from datetime import datetime
        wind_xarrays['METADATA'].attrs['start_datetime'] = datetime.strptime(wind_xarray.time_coverage_start, '%Y-%m-%dT%H:%M:%S Z')
        wind_xarrays['METADATA'].attrs['end_datetime'] = datetime.strptime(wind_xarray.time_coverage_end, '%Y-%m-%dT%H:%M:%S Z')

    return wind_xarrays
