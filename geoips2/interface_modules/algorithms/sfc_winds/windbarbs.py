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

''' Data manipulation steps for surface winds products.

    This algorithm expects surface wind speeds in units of kts
'''

import logging

LOG = logging.getLogger(__name__)

alg_func_type = 'list_numpy_to_numpy'


def windbarbs(arrays, output_data_range, input_units=None, output_units=None,
              min_outbounds='crop', max_outbounds='crop', norm=False, inverse=False):
    ''' Data manipulation steps for "windbarbs" product algorithm.

    This algorithm expects input windspeed with units "kts" and returns in "kts"

    Args:
        data (list[numpy.ndarray]) : 
            * list of numpy.ndarray or numpy.MaskedArray of channel data, in order of sensor "channels" list
            * kts
        output_data_range (list[float]) :
            * list of min and max value for wind speeds (kts)
        input_units (str) : DEFAULT None
            * Units of input data, for applying necessary conversions
        output_units (str) : DEFAULT None
            * Units of output data, for applying necessary conversions
        min_outbounds (str) : DEFAULT 'crop'
            * Method to use when applying bounds.  Valid values are:
                * retain: keep all pixels as is
                * mask: mask all pixels that are out of range
                * crop: set all out of range values to either min_val or max_val as appropriate
        max_outbounds (str) : DEFAULT 'crop'
            * Method to use when applying bounds.  Valid values are:
                * retain: keep all pixels as is
                * mask: mask all pixels that are out of range
                * crop: set all out of range values to either min_val or max_val as appropriate
        norm (bool) : DEFAULT True
            * Boolean flag indicating whether to normalize (True) or not (False)
                * If True, returned data will be in the range from 0 to 1
                * If False, returned data will be in the range from min_val to max_val
        inverse (bool) : DEFAULT True
            * Boolean flag indicating whether to inverse (True) or not (False)
                * If True, returned data will be inverted
                * If False, returned data will not be inverted

    Returns:
        numpy.ndarray : numpy.ndarray or numpy.MaskedArray of appropriately scaled channel data, dstacked as follows:
                           * (spd, direction, rain_flag)
                           * spd in kts
                           * direction in degrees
                           * rain_flag 0 or 1
    '''

    import numpy
    spd = arrays[0]
    direction = arrays[1]
    if len(arrays) > 2:
        rain_flag = arrays[2]
    else:
        rain_flag = numpy.zeros(arrays[1].shape)

    from geoips2.data_manipulations.conversions import unit_conversion
    spd = unit_conversion(spd, input_units, output_units)

    from geoips2.data_manipulations.corrections import apply_data_range
    spd = apply_data_range(spd,
                           min_val=output_data_range[0], max_val=output_data_range[1],
                           min_outbounds=min_outbounds, max_outbounds=max_outbounds,
                           norm=norm, inverse=inverse)
    return numpy.ma.dstack((spd, direction, rain_flag)).squeeze()


