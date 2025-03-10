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

''' Module containing wind speed colormap with transitions at 34, 50, 64, and 80 '''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'linear_segmented'


def wind_radii_transitions(data_range=[0, 200]):
    ''' Generate appropriate matplotlib colors for plotting standard wind speeds. wind_radii_transitions
        contains hard coded transition values for different colors, in order to have consistent imagery across all
        sensors / products

    Args:
        data_range (list[float]): Default [0, 200], Min and max value for colormap.
                                  Ensure the data range matches the range of the algorithm specified for use with this colormap

    Returns:
        dictionary : Dictionary of matplotlib plotting parameters, to ensure consistent image output
    '''

    from geoips2.image_utils.colormap_utils import create_linear_segmented_colormap
    min_wind_speed = data_range[0]
    max_wind_speed = data_range[1]
    transition_vals = [(min_wind_speed, 34),
                       (34, 50),
                       (50, 64),
                       (64, 80),
                       # (64, 72),
                       # (72, 80),
                       (80, 100),
                       (100, 120),
                       (120, 150),
                       (150, max_wind_speed)]
    transition_colors = [('lightblue', 'blue'),
                         ('yellow', 'orange'),
                         ('red', 'red'),

                         # ('thistle', 'thistle'),
                         # ('firebrick', 'firebrick'),
                         # ('fuchsia', 'fuchsia'),
                         # ('mediumvioletred', 'mediumvioletred'),
                         ('rebeccapurple', 'rebeccapurple'),

                         # ('purple', 'rebeccapurple'),
                         # ('rebeccapurple', 'rebeccapurple'),
                         # ('mediumvioletred', 'mediumvioletred'),
                         ('palevioletred', 'palevioletred'),

                         ('silver', 'silver'),
                         ('gray', 'gray'),
                         ('dimgray', 'dimgray')]

    ticks = [xx[0] for xx in transition_vals]

    min_wind_speed = transition_vals[0][0]
    max_wind_speed = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('windspeed_cmap',
                                                min_wind_speed,
                                                max_wind_speed,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_wind_speed, vmax=max_wind_speed)

    cbar_label = 'Surface Wind (knots)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True}

    # return cbar, min_wind_speed, max_wind_speed
    return mpl_colors_info
