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

''' Routines for converting between units '''
# Python Standard Libraries
import logging

# Installed Libraries
import numpy

KtoC_conversion = -273.15

LOG = logging.getLogger(__name__)


def unit_conversion(data_array, input_units=None, output_units=None):
    ''' Convert array in units 'input_units' to units 'output_units


    Args:
        data_array (ndarray) : numpy.ndarray or numpy.MaskedArray of data values to be converted
        input_units (str, optional) : DEFAULT None, Units of input data array
        output_units (str, optional) : DEFAULT None, Units of output data array

    Returns:
        (MaskedArray) : Return numpy.ma.MaskedArray, with units converted from 'input_units' to 'output_units'
    '''

    if input_units and output_units and input_units != output_units:
        from geoips2.data_manipulations.corrections import apply_offset
        valid_units = ['Kelvin', 'celsius']
        if input_units not in valid_units:
            raise ValueError(f'Input units must be one of {valid_units}')
        if output_units not in valid_units:
            raise ValueError(f'Output units must be one of {valid_units}')

        if input_units == 'Kelvin' and output_units == 'celsius':
            data_array = apply_offset(data_array, KtoC_conversion)

        if input_units == 'celsius' and output_units == 'Kelvin':
            data_array = apply_offset(data_array, -KtoC_conversion)

    return data_array
