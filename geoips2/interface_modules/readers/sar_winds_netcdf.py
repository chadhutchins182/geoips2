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


def read_sar_data(wind_xarray):
    ''' Reformat SAR xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    # Setting standard geoips attributes
    LOG.info('Reading SAR data')
    wind_xarray.attrs['source_name'] = 'sar-spd'
    if 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'sentinel-1a':
        wind_xarray.attrs['platform_name'] = 'sentinel-1'
    elif 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'rcm-1':
        wind_xarray.attrs['platform_name'] = 'rcm-1'
    elif 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'rcm-2':
        wind_xarray.attrs['platform_name'] = 'rcm-2'
    elif 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'rcm-3':
        wind_xarray.attrs['platform_name'] = 'rcm-3'
    elif 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'radarsat-2':
        wind_xarray.attrs['platform_name'] = 'radarsat-2'
    else:
        raise ValueError(f'Unsupported satellite name for SAR data: {wind_xarray.platform}')
    wind_xarray.attrs['interpolation_radius_of_influence'] = 3000
    # For resampling to a minimum-sized grid
    wind_xarray.attrs['sample_distance_km'] = 3.0
    wind_xarray.attrs['sample_pixels_x'] = 300
    wind_xarray.attrs['sample_pixels_y'] = 300
    wind_xarray.attrs['minimum_coverage'] = 0
    wind_xarray.attrs['granule_minutes'] = 0.42
    wind_xarray.attrs['data_provider'] = 'star'
    if 'acknowledgment' in wind_xarray.attrs and 'NOAA' in wind_xarray.acknowledgment:
        wind_xarray.attrs['data_provider'] = 'star'
    # Used for tc filenames / text files

    LOG.info('Shape: %s', wind_xarray['sar_wind'].shape)
    # setting wind_speed_kts appropriately
    wind_xarray['wind_speed_kts'] = wind_xarray['sar_wind'] * MS_TO_KTS
    wind_xarray['wind_speed_kts'].attrs = wind_xarray['sar_wind'].attrs
    wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'
    import xarray
    import numpy
    wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.mask == -1, wind_xarray.wind_speed_kts, numpy.nan)

    # Set lat/lons appropriately
    wind_xarray = wind_xarray.rename({'latitude': 'latitude', 'longitude': 'longitude'})

    # Set timestamp appropriately
    # Get the full array of timestamps.  pandas is much better with time series.
    wind_pandas = wind_xarray.to_dataframe()

    # This worked with xarray version 0.16.1
    # wind_xarray['timestamp'] = wind_pandas['acquisition_time'][:, 5, :].to_xarray().transpose()

    # Make sure it grabs the right ones, no matter which order x, y, and xfit are in.
    # Later versions (0.18.0) of xarray can have different orders -
    # ensure we use labels, not explicit locations
    timestamp_array = wind_pandas['acquisition_time'].to_xarray()[dict(x=slice(None),
                                                                       y=slice(None),
                                                                       xfit=5)].transpose('y', 'x')
    # Remove the xfit coordinate - no longer needed
    wind_xarray['timestamp'] = timestamp_array.reset_coords('xfit', drop=True)

    wind_xarray = wind_xarray.set_coords(['timestamp'])
    wind_xarray['sigma'] = xarray.where(wind_xarray.sigma == 0, numpy.nan, wind_xarray.sigma)
    # This is not correct - should be -35 to -20, need to find documentation for deriving NRCS from sigma
    wind_xarray['nrcs'] = 10 * numpy.log10(wind_xarray.sigma)
    return [wind_xarray]


def sar_winds_netcdf(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):
    ''' Read SAR derived winds from netcdf data.

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
    wind_xarray.attrs['data_provider'] = 'unknown'
    wind_xarray.attrs['source_name'] = 'unknown'
    wind_xarray.attrs['platform_name'] = 'unknown'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 'unknown'
    wind_xarray.attrs['original_source_filenames'] = [basename(fname)]
    wind_xarray.attrs['sample_distance_km'] = 'unknown'

    LOG.info('Read data from %s', fname)

    if hasattr(wind_xarray, 'source') and 'SAR' in wind_xarray.source\
       and hasattr(wind_xarray, 'title') and 'SAR' in wind_xarray.title:
        wind_xarrays = []
        columns = None
        for fname in fnames:
            LOG.info('    Reading file %s', fname)
            wind_xarray = xarray.open_dataset(str(fname))
            LOG.info('        rows: %s, columns: %s', wind_xarray.rows, wind_xarray.columns)
            if columns is None:
                columns = wind_xarray.columns
            if columns == wind_xarray.columns:
                wind_xarrays += read_sar_data(wind_xarray)
            else:
                LOG.info('            COLUMNS DOES NOT MATCH, NOT APPENDING')
        if len(fnames) == 1:
            wind_xarrays = {'WINDSPEED': wind_xarrays[0]}
        else:
            final_xarray = xarray.Dataset()
            import numpy
            lat_array = xarray.DataArray(numpy.vstack([curr_xarray.latitude.to_masked_array()
                                                       for curr_xarray in wind_xarrays]))
            lon_array = xarray.DataArray(numpy.vstack([curr_xarray.longitude.to_masked_array()
                                                       for curr_xarray in wind_xarrays]))
            timestamp_array = xarray.DataArray(numpy.vstack([curr_xarray.timestamp.to_masked_array()
                                                             for curr_xarray in wind_xarrays]))
            wspd_array = xarray.DataArray(numpy.vstack([curr_xarray.wind_speed_kts.to_masked_array()
                                                       for curr_xarray in wind_xarrays]))
            sigma_array = xarray.DataArray(numpy.vstack([curr_xarray.sigma.to_masked_array()
                                                       for curr_xarray in wind_xarrays]))
            final_xarray['latitude'] = lat_array
            final_xarray['longitude'] = lon_array
            final_xarray['timestamp'] = timestamp_array
            final_xarray['wind_speed_kts'] = wspd_array
            final_xarray['sigma'] = sigma_array
            final_xarray.attrs = wind_xarrays[0].attrs

            wind_xarrays = {'WINDSPEED': final_xarray}

    for wind_xarray in wind_xarrays.values():

        if not hasattr(wind_xarray, 'minimum_coverage'):
            wind_xarray.attrs['minimum_coverage'] = 20

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
        wind_xarrays['METADATA'].attrs['start_datetime'] = datetime.strptime(wind_xarray.time_coverage_start, '%Y%m%dT%H%M%S')
        wind_xarrays['METADATA'].attrs['end_datetime'] = datetime.strptime(wind_xarray.time_coverage_end, '%Y%m%dT%H%M%S')

    return wind_xarrays
