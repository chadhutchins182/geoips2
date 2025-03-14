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

''' Module containing colormap for ~89GHz PMW products, highlighting weak convection'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'linear_segmented'


def cmap_89HW(data_range=[220.0, 280.0]):
    ''' Colormap for displaying ~89GHz PMW data for weak TCs.
    
    Args:
        data_range (list[float]): Min and max value for colormap.
                                  Ensure the data range matches the range of the algorithm specified for use with this colormap
                                  The 89HW colormap MUST include 220 and 265
    Returns:
        dictionary : Dictionary of matplotlib plotting parameters, to ensure consistent image output
    '''

    min_tb = data_range[0]
    max_tb = data_range[1]

    if min_tb > 220 or max_tb < 265:
        raise('89HW TB range must include 220 and 265')

    # use the TC 89 GHz legacy color table for 89HW (Weak TCs)  
    from geoips2.image_utils.colormap_utils import create_linear_segmented_colormap
    transition_vals = [(min_tb, 220.1),
                       (220.1, 240),
                       (240, 249),
                       (249, 264),
                       (264, max_tb)]
    transition_colors = [('black', 'black'),
                         ('#A4641A', '#FC0603'),
                         ('#F4CD03', '#F2F403'),
                         ('#8CF303', '#0FB503'),
                         ('#06DCFD', '#0708B5')
                         ]

    #ticks = [xx[0] for xx in transition_vals]

    #special selection of label

    ticks = [220, 230, 240, 250, 260, 270, 280]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('cmap_89hw',
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
