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

'''Standard TC filename production'''

# Python Standard Libraries
import logging

from geoips2.filenames.base_paths import PATHS as gpaths
from os.path import join as pathjoin

LOG = logging.getLogger(__name__)

filename_type = 'data'


def geoips_netcdf_fname(area_def, xarray_obj, product_names, coverage=None, output_type='nc', output_type_dir=None,
                        product_dir=None, product_subdir=None, source_dir=None, basedir=None):

    if basedir is None:
        basedir = gpaths['PRECALCULATED_DATA_PATH']
    ncdf_fname = assemble_geoips_netcdf_fname(basedir=basedir,
                                              product_name='_'.join(product_names),
                                              source_name=xarray_obj.source_name,
                                              platform_name=xarray_obj.platform_name,
                                              sector_name=xarray_obj.area_definition.area_id,
                                              product_datetime=xarray_obj.start_datetime)


    return ncdf_fname


def assemble_geoips_netcdf_fname(basedir, product_name, source_name=None, platform_name=None,
                                 sector_name=None, product_datetime=None, set_subpath=None, time_format='%H%M%S'):
    ''' Produce full output product path from product / sensor specifications.
        netcdf paths are of the format:
          <basedir>/<product_name>/<source_name>/<platform_name>/<sector_name>/date{%Y%m%d}
        netcdf filenames are of the format:
          <date{%Y%m%d>.<time{%H%M%S}>.<platform_name>.<product_name>.<sector_name>.nc
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==============----+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | product_name:    | *str*     | Name of product                                   |
    +------------------+-----------+---------------------------------------------------+
    | source_name:     | *str*     | Name of data source (sensor)                      |
    +------------------+-----------+---------------------------------------------------+
    | platform_name:   | *str*     | Name of platform (satellite)                      |
    +------------------+-----------+---------------------------------------------------+
    | coverage:        | *float*   | Image coverage, float between 0.0 and 100.0       |
    +------------------+-----------+---------------------------------------------------+
    | product_datetime:| *datetime*| Datetime object - start time of data used to      |
    |                  |           |     generate product                              |
    +------------------+-----------+---------------------------------------------------+
    '''

    if set_subpath:
        path = pathjoin(basedir,set_subpath)
    else:
        path = basedir
        if product_name is not None:
            path = pathjoin(path, product_name)
        if source_name is not None:
            path = pathjoin(path, source_name)
        if platform_name is not None:
            path = pathjoin(path, platform_name)
        if sector_name is not None:
            path = pathjoin(path, sector_name)
        if product_datetime is not None:
            path = pathjoin(path, product_datetime.strftime('%Y%m%d'))
    fname = ''
    path_parts = []
    if product_datetime is not None:
        path_parts.extend([product_datetime.strftime('%Y%m%d'), product_datetime.strftime(time_format)])
    if platform_name is not None:
        path_parts.extend([platform_name])
    if product_name is not None:
        path_parts.extend([product_name])
    if sector_name is not None:
        path_parts.extend([sector_name])
    fname = '.'.join(path_parts+['nc'])

    return pathjoin(path, fname)
