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

''' Module containing tpw_cimss ASCII palette based colormap'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'ascii'


def tpw_purple():
    ''' Colormap for displaying data using purple TPW ascii colormap.

    ASCII palette is found in image_utils/ascii_palettes/tpw_purple.txt
    Data range of ASCII palette is 5 to 65 mm, with transitions at 15, 25, 35, 45, and 55
    
    Returns:
        dictionary : Dictionary of matplotlib plotting parameters, to ensure consistent image output
    '''

    from os.path import basename as pathbasename, join as pathjoin
    from geoips2.filenames.base_paths import PATHS as gpaths
    from geoips2.image_utils.colormap_utils import from_ascii
    from matplotlib.colors import Normalize
    min_val = 5
    max_val = 65

    mpl_colors_info = {'cmap': from_ascii(pathjoin(gpaths['GEOIPS2'], 'geoips2',
                                          'image_utils', 'ascii_palettes', 'tpw_purple.txt')),
                       'norm': Normalize(vmin=min_val, vmax=max_val),
                       'cbar_ticks': [min_val, 15, 25, 35, 45, 55, max_val],
                       'cbar_tick_labels': None,
                       'cbar_label': r'TPW (mm)',
                       'boundaries': None,
                       'cbar_spacing': 'proportional',
                       'colorbar': True,
                       'cbar_full_width': True}
    return mpl_colors_info
