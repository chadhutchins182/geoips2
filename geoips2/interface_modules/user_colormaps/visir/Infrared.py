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

''' Module containing Infrared algorithm colormap'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'linear_segmented'


def Infrared(data_range=[-90, 30]):
    ''' Colormap developed for displaying algorithms/visir/Infrared.py processed data.
    
    Args:
        data_range (list[float]): Min and max value for colormap.
                                  Ensure the data range matches the range of the algorithm specified for use with this colormap
                                  The Infrared colormap MUST include -90 and 30
    Returns:
        dictionary : Dictionary of matplotlib plotting parameters, to ensure consistent image output
    '''

    min_tb = int(data_range[0])
    max_tb = int(data_range[1])

    # for Infrared images at 11 um.  Unit: Celsius

    if min_tb > -90 or max_tb < 30:
        raise('Infrared TB range must include -90 and 30')

    from geoips2.image_utils.colormap_utils import create_linear_segmented_colormap
    transition_vals = [(min_tb, -80),
                       (-80, -70),
                       (-70, -50),
                       (-50, -40),
                       (-40, -30),
                       (-30, -15),
                       (-15,   0),
                       (  0,  15),
                       ( 15, max_tb)]
    transition_colors = [('darkorange', 'yellow'),
                         ('darkred', 'red'),
                         ('green', 'palegreen'),
                         ('navy', 'royalblue'),
                         ('royalblue','deepskyblue'),
                         ('whitesmoke', 'silver'),
                         ('silver','grey'),
                         ('grey','dimgrey'),
                         ('dimgrey', 'black')]

    #ticks = [int(xx[0]) for xx in transition_vals]

    #special selection of label

    ticks = [min_tb, -80, -70, -60,-50, -40, -30, -20, -10, 0, 10, 20, max_tb]
    
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]
    ticks = ticks + [int(max_tb)]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('IR_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = r'11$\mu$m BT ($^\circ$C)'

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
