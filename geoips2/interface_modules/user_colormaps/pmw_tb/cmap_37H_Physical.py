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

''' Module containing colormap for ~37GHz PMW products'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'linear_segmented'


def cmap_37H_Physical(data_range=[125, 310]):
    ''' Colormap for displaying ~37GHz PMW data.
    
    Args:
        data_range (list[float]): Default [125, 310], Min and max value for colormap.
                                  Ensure the data range matches the range of the algorithm specified for use with this colormap
                                  The 37GHz colormap MUST include 180 and 280
    Returns:
        dictionary : Dictionary of matplotlib plotting parameters, to ensure consistent image output
    '''

    min_tb = data_range[0]
    max_tb = data_range[1]

    if min_tb > 125 or max_tb < 300:
        raise('37GHz TB range must include 125 and 300')

    from geoips2.image_utils.colormap_utils import create_linear_segmented_colormap

    transition_vals = [(min_tb, 125),
                       (125, 150),
                       (150, 175),
                       (175, 212),
                       (212, 230),
                       (230, 250),
                       (250, 265),
                       (265, 280),
                       (280, max_tb)]
    transition_colors = [('orange', 'chocolate'),
                         ('chocolate', 'indianred'),
                         ('indianred', 'firebrick'),
                         ('firebrick', 'red'),
                         ('gold', 'yellow'),
                         ('lime', 'limegreen'),
                         ('deepskyblue', 'blue'),
                         ('navy', 'slateblue'),
                         ('magenta', 'white')]

    ticks = [xx[0] for xx in transition_vals]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]
    ticks = ticks + [int(max_tb)]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('cmap_37H_Physical',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

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
                       'colorbar': True,
                       'cbar_full_width': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info

