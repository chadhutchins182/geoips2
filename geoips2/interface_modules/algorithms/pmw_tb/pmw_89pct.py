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

''' Data manipulation steps for "89pct" product.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin
'''

import logging

LOG = logging.getLogger(__name__)

alg_func_type = 'list_numpy_to_numpy'


def pmw_89pct(arrays, output_data_range, min_outbounds='crop', max_outbounds='mask', norm=False, inverse=False):
    ''' Data manipulation steps for "89pct" product algorithm.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin, and returns degrees Kelvin

    Args:
        arrays (list[numpy.ndarray]) : 
            * list of numpy.ndarray or numpy.MaskedArray of channel data and other variables, in order of sensor "variables" list
            * Channel data: Degrees Kelvin

    Returns:
        numpy.ndarray : numpy.ndarray or numpy.MaskedArray of appropriately scaled channel data,
                        in degrees Kelvin.
    '''

    h89 = arrays[0]
    v89 = arrays[1]

    out = (1.7*v89)-(0.7*h89)

    from geoips2.data_manipulations.corrections import apply_data_range
    data = apply_data_range(out,
                            min_val=output_data_range[0], max_val=output_data_range[1],
                            min_outbounds=min_outbounds, max_outbounds=max_outbounds,
                            norm=norm, inverse=inverse)

    return data


