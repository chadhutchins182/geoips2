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

''' Interface Under Development.  Please provide feedback to geoips@nrlmry.navy.mil

    Wrapper functions for geoips2 colormap interfacing.

    Once all related wrapper functions are finalized,
    this module will be moved to the geoips2/stable sub-package.
'''

import logging
import collections
from importlib import import_module
LOG = logging.getLogger(__name__)

from geoips2.geoips2_utils import find_entry_point, list_entry_points


### Colormap functions ###
def is_valid_cmap(cmap_func_name):
    ''' Interface Under Development, please provide feedback to geoips@nrlmry.navy.mil

    Check that the requested colormap function has the correct call signature.
        Return values should be as specified below, but are not programmatically verified.

    Args:
        cmap_func_name (str) : Desired cmap function (ie, 'visir.IR_BD', 'pmw_tb.cmap_89H', 'cmap_rgb', etc)

    Returns:
        (bool) : True if 'cmap_func_name' has the appropriate call signature
                 False if cmap function:
                        does not contain all required arguments
                        does not contain all required keyword arguments

    Colormap type currently found in
        <geoips2_package>.image_utils.user_colormaps.*.<cmap_func_name>.colormap_type
            OR
        <geoips2_package>.image_utils.user_colormaps.<cmap_func_name>.colormap_type

    Colormap functions currently defined in
        <geoips2_package>.image_utils.user_colormaps.*.<cmap_func_name>.<cmap_func_name>
            OR
        <geoips2_package>.image_utils.user_colormaps.<cmap_func_name>.<cmap_func_name>
    and requested within the product parameters dictionary
        See geoips2.dev.cmap.check_product_params

    cmap_func types currently one of:

           'rgb' : call signature <cmap_func_name>()
                        return value: mpl_colors_info dict
           'ascii' : call signature <cmap_func_name>()
                        return value: mpl_colors_info dict
           'linear_segmented' : call signature <cmap_func_name>()
                        return value: mpl_colors_info dict

    Return dictionary:
    mpl_colors_info {'cmap': <matplotlib colormap object>,
                     'norm': <matplotlib norm object>,
                     'cbar_ticks': <list of tick values for colorbar>, 
                     'cbar_label': <str label for colorbar>, 
                     'boundaries': <matplotlib boundaries object>, 
                     'cbar_spacing': <'uniform' or 'proportional'>, 
                     'colorbar': <bool>, 
                     'cbar_full_width': <bool>}

    For package based colormap functions:
        See geoips2.dev.cmap.get_cmap
        See geoips2.dev.cmap.get_cmap_type
        See geoips2.dev.cmap.list_cmaps_by_type
    
    For product based colormap functions:
        See geoips2.dev.cmap.get_cmap
        See geoips2.dev.cmap.get_cmap_name
        See geoips2.dev.cmap.get_cmap_args
    '''
    cmap_func = get_cmap(cmap_func_name)
    # If this is __init__ (no __code__ attr), skip it
    if not hasattr(cmap_func, '__code__'):
        return False
    required_args = {'rgb': [],
                     'ascii': [],
                     'linear_segmented': [],
                     'linear_norm': [],
                     'product_based': [],
                     'explicit': [],
                     'builtin_matplotlib_cmap': ['data_range']}
    required_kwargs = {'rgb': [],
                       'ascii': [],
                       'linear_segmented': ['data_range'],
                       'linear_norm': ['data_range'],
                       'product_based': ['product_name', 'data_range'],
                       'explicit': [],
                       'builtin_matplotlib_cmap': ['cmap_name', 'cbar_label', 'create_colorbar']}

    cmap_func_type = get_cmap_type(cmap_func_name)

    if cmap_func_type not in required_args:
        raise TypeError(f"INVALID CMAP FUNC {cmap_func_name}:\n"
                        f"Unknown output type {cmap_func_type}, allowed types: {required_args.keys()}\n"
                        f"Either add '{cmap_func_type}' to list of supported types\n"
                        f"in output.is_valid_cmap.required_args\n"
                        f"or update '{cmap_func.__module__}' to a supported type")
    if cmap_func_type not in required_kwargs:
        raise TypeError(f"INVALID CMAP FUNC {cmap_func_name}:\n"
                        f"Unknown output type {cmap_func_type}, allowed types: {required_kwargs.keys()}\n"
                        f"Either add '{cmap_func_type}' to list of supported types in\n"
                        f"output.is_valid_cmap.required_args\n"
                        f"or update '{cmap_func.__module__}' to a supported type")

    num_args = len(required_args[cmap_func_type])
    num_kwargs = len(required_kwargs[cmap_func_type])

    cmap_func_vars = cmap_func.__code__.co_varnames
    cmap_func_args = cmap_func_vars[0:num_args]
    cmap_func_kwargs = cmap_func_vars[num_args:num_args+num_kwargs]

    # Check for required call signature arguments
    if not set(required_args[cmap_func_type]).issubset(set(cmap_func_args)):
        LOG.error("INVALID CMAP FUNC '%s': '%s' cmap func type must have required arguments: '%s'",
                  cmap_func_name, cmap_func_type, cmap_func_args[cmap_func_type])
        return False

    # Check for optional call signature keyword arguments
    if not set(required_kwargs[cmap_func_type]).issubset(set(cmap_func_kwargs)):
        LOG.error("INVALID CMAP FUNC '%s': '%s' cmap_func type must have kwargs: '%s'",
                  cmap_func_name, cmap_func_type, required_kwargs[cmap_func_type])
        return False

    return True


def get_cmap(cmap_func_name):
    ''' Interface Under Development, please provide feedback to geoips@nrlmry.navy.mil

    Retrieve the requested colormap function

    See: geoips2.dev.cmap.is_valid_cmap for full list of supported cmap function call signatures and return values

    Args:
        cmap_func_name (str) : Desired cmap function (ie, 'visir.IR_BD', 'pmw_tb.cmap_89H', 'cmap_rgb', etc)

    Returns:
        (<cmap function>) : Colormap function
    '''
    return find_entry_point('user_colormaps', cmap_func_name)


def get_cmap_type(cmap_func_name):
    ''' Interface Under Development, please provide feedback to geoips@nrlmry.navy.mil

    Retrieve type of the requested colormap function.
    Type specifies the required call signature and return values

    Args:
        cmap_func_name (str) : Desired cmap function (ie, 'visir.IR_BD', 'pmw_tb.cmap_89H', 'cmap_rgb', etc)

    Returns:
        (str) : Colormap function type
    '''
    cmap_func = find_entry_point('user_colormaps', cmap_func_name)
    return getattr(import_module(cmap_func.__module__), 'cmap_type')


def list_cmaps_by_type():
    ''' Interface Under Development, please provide feedback to geoips@nrlmry.navy.mil

    List all available colormap functions within the current GeoIPS instantiation, sorted by cmap_type

    Colormap function "type" determines exact required call signatures and return values

    See geoips2.dev.cmap.is_valid_cmap? for a list of available colormap function types and associated call signatures / return values.
    See geoips2.dev.cmap.get_cmap(cmap_func_name) to retrieve the requested colormap function
    See geoips2.dev.cmap.get_cmap_type(cmap_func_name) to retrieve the requested colormap function type

    Returns:
        (dict) : Dictionary with all colormap function types as keys, and associated colormap function names (str) as values.
    '''
    all_colormaps = collections.defaultdict(list)
    for colormap in list_entry_points('user_colormaps'):
        cmap_type = get_cmap_type(colormap)
        if colormap not in all_colormaps[cmap_type]:
            all_colormaps[cmap_type].append(colormap)
    return all_colormaps


def test_cmap_interface():
    ''' Finds and opens every cmap func available within the current geoips2 instantiation

    See geoips2.dev.cmap.is_valid_cmap? for a list of available cmap func types and associated call signatures / return values.
    See geoips2.dev.cmap.get_cmap(cmap_func_name) to retrieve the requested cmap func

    Returns:
        (list) : List of all successfully opened geoips2 cmap funcs
    '''

    curr_names = list_cmaps_by_type()
    # out_dict = {'by_type': curr_names, 'validity_check': {}, 'func_type': {}, 'func': {}, 'cmaps': {}, 'cmap_args': {}, 'cmap_func_names': {}}
    out_dict = {'by_type': curr_names, 'validity_check': {}, 'func_type': {}, 'func': {}}
    for curr_type in curr_names:
        for curr_name in curr_names[curr_type]:
            out_dict['validity_check'][curr_name] = is_valid_cmap(curr_name)
            out_dict['func'][curr_name] = get_cmap(curr_name)
            out_dict['func_type'][curr_name] = get_cmap_type(curr_name)

    # from geoips2.dev.product import list_products_by_source, get_cmap_name, get_cmap_from_product, get_cmap_args
    # product_params_dicts = list_products_by_source()
    # for source_name in product_params_dicts:
    #     for product_name in product_params_dicts[source_name]:
    #         cmap_func_name = get_cmap_name(product_name, source_name)
    #         out_dict['cmap_names'][cmap_func_name] = cmap_func_name
    #         out_dict['cmaps'][cmap_func_name] = get_cmap_from_product(product_name, source_name)
    #         out_dict['cmap_args'][cmap_func_name] = get_cmap_args(product_name, source_name)

    return out_dict
