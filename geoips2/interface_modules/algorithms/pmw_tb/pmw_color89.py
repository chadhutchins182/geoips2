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

''' Data manipulation steps for "color89" product.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin
'''

import logging

LOG = logging.getLogger(__name__)

alg_func_type = 'list_numpy_to_numpy'


def pmw_color89(arrays):
    ''' Data manipulation steps for "color89" product algorithm.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin,
    and returns red green and blue gun arrays.

    Args:
        arrays (list[numpy.ndarray]) : 
            * list of numpy.ndarray or numpy.MaskedArray of channel data and other variables, in order of sensor "variables" list
            * Channel data: Degrees Kelvin

    Returns:
        numpy.ndarray : numpy.ndarray or numpy.MaskedArray of qualitative RGBA image output
    '''

    h89 = arrays[0]
    v89 = arrays[1]

    from geoips2.data_manipulations.corrections import apply_data_range, apply_gamma
    red = 1.818*v89 - 0.818*h89
    red = apply_data_range(red, 220.0, 310.0,
                           min_outbounds='crop', max_outbounds='crop',
                           norm=True, inverse=True)
    red = apply_gamma(red, 1.0)

    grn = (h89 - 240.0) / (300.0 - 240.0)
    grn = apply_data_range(grn, 0.0, 1.0,
                           min_outbounds='crop', max_outbounds='crop',
                           norm=True, inverse=False)
    grn = apply_gamma(grn, 1.0)

    blu = (v89 - 270.0) / (290.0 - 270.0)
    blu = apply_data_range(blu, 0.0, 1.0,
                           min_outbounds='crop', max_outbounds='crop',
                           norm=True, inverse=False)
    blu = apply_gamma(blu, 1.0)

    from geoips2.image_utils.mpl_utils import alpha_from_masked_arrays, rgba_from_arrays
    alp = alpha_from_masked_arrays([red, grn, blu])
    rgba = rgba_from_arrays(red, grn, blu, alp)
    return rgba
