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

''' Introspection functions on data arrays'''

import logging
import numpy

LOG = logging.getLogger(__name__)


def percent_unmasked(data_array):
    ''' Specify coverage based on current data type
        Parameters:
            data_array (numpy.ma.MaskedArray) : Final processed array from which to determine coverage
        Returns:
            (float) representing percent coverage
    '''

    return 100 * (float(numpy.ma.count(data_array)) / data_array.size)
