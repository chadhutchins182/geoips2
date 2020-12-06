# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
# # #  # # #
# # # Author: # # #
# # # Naval Research Laboratory, Marine Meteorology Division # # #
# # #  # # #
# # # This program is free software: you can redistribute it and/or modify it under # # #
# # # the terms of the NRLMMD License included with this program.  If you did not # # #
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
# # # information. # # #
# # #  # # #
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
# # # included license for more details. # # #

'''Read derived surface winds from SAR, SMAP, SMOS, and AMSR netcdf data.'''
import logging
LOG = logging.getLogger(__name__)

MS_TO_KTS = 1.94384


def sfc_winds_text(fname, metadata_only=False):
    ''' Read one of SAR, SMAP, SMOS, AMSR derived winds from netcdf data.
        Parameters:
            fname (str): Required full path to text file
        Returns:
            xarray.Dataset with required Variables and Attributes:
                Variables: 'latitude', 'longitude', 'timestamp', 'wind_speed_kts'
                Attributes: 'source_name', 'platform_name', 'data_provider', 'interpolation_radius_of_influence'
                            'start_datetime', 'end_datetime'
    '''
    import numpy
    import pandas
    LOG.info('Reading file %s', fname)
    data = numpy.loadtxt(fname, dtype=str, skiprows=0)

    if data[0][0] == 'SAR':
        source_name = 'sar-spd'
        platform_name = 'sen1'
        interpolation_roi = 3000
        data_provider = 'star'
    elif data[0][0] == 'SMAP':
        source_name = 'smap-spd'
        platform_name = 'smap'
        interpolation_roi = 15000
        data_provider = 'rss'
    elif data[0][0] == 'SMOS':
        source_name = 'smos-spd'
        platform_name = 'smos'
        interpolation_roi = 25000
        data_provider = 'esa'
    elif data[0][0] == 'AMSR':
        source_name = 'amsr2'
        platform_name = 'gcom-w1'
        interpolation_roi = 10000
        data_provider = 'star'

    LOG.info('Making full dataframe')
    # make a data frame
    columns = ['dataType', 'latitude', 'longitude', 'wind_speed_kts', 'timestamp']
    wind_xarray = pandas.DataFrame(data=data, columns=columns)

    LOG.info('Converting lat to numeric')
    # make appropriate data types
    wind_xarray['longitude'] = pandas.to_numeric(wind_xarray['longitude'], errors='coerce')
    LOG.info('Converting lon to numeric')
    wind_xarray['latitude'] = pandas.to_numeric(wind_xarray['latitude'], errors='coerce')
    LOG.info('Converting windspeed to numeric')
    wind_xarray['wind_speed_kts'] = pandas.to_numeric(wind_xarray['wind_speed_kts'], errors='coerce')
    LOG.info('Converting to timestamp to datetime')

    # This is ORDERS OF MAGNITUDE slower than giving the format directly. Seconds vs minutes
    # wind_xarray['timestamp'] = pandas.to_datetime(wind_xarray['timestamp'],
    #                                                infer_datetime_format=True, errors='coerce')
    wind_xarray['timestamp'] = pandas.to_datetime(wind_xarray['timestamp'], format='%Y%m%d%H%M', errors='coerce')

    wind_xarray = wind_xarray.to_xarray()

    wind_xarray.attrs['source_name'] = source_name
    wind_xarray.attrs['platform_name'] = platform_name
    wind_xarray.attrs['start_datetime'] = wind_xarray.to_dataframe()['timestamp'].min().to_pydatetime()
    wind_xarray.attrs['end_datetime'] = wind_xarray.to_dataframe()['timestamp'].max().to_pydatetime()
    wind_xarray.attrs['data_provider'] = data_provider
    # 20000 leaves gaps
    wind_xarray.attrs['interpolation_radius_of_influence'] = interpolation_roi

    # These text files store wind speeds natively in kts
    wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'
    wind_xarray['longitude'].attrs['units'] = 'degrees'
    wind_xarray['latitude'].attrs['units'] = 'degrees'

    return wind_xarray
