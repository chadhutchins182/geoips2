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

''' Module containing matplotlib information for RGB or RGBA imagery'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'rgb'


def cmap_rgb():
    ''' For rgb imagery, we require no color information (it is entirely specified by the RGB(A) arrays)
    
    Args:
        No arguments

    Returns:
        mpl_colors_info (dict) Specifies matplotlib Colors parameters for use in both plotting and colorbar generation
                               For RGBA arrays, all fields are "None"
    '''
    mpl_colors_info = {'cmap': None,
                       'norm': None,
                       'cbar_ticks': None,
                       'cbar_tick_labels': None,
                       'cbar_label': None,
                       'boundaries': None,
                       'cbar_spacing': 'proportional',
                       'colorbar': False}
    return mpl_colors_info
