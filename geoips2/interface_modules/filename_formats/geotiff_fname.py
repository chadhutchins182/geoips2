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

LOG = logging.getLogger(__name__)

filename_type = 'standard'


def geotiff_fname(area_def, xarray_obj, product_name, coverage, output_type='tif', output_type_dir=None,
                  product_dir=None, product_subdir=None, source_dir=None, basedir=gpaths['ANNOTATED_IMAGERY_PATH']):

    from geoips2.dev.filename import get_filenamer
    from geoips2.sector_utils.utils import is_sector_type
    if is_sector_type(area_def, 'tc'):
        fname_func = get_filenamer('tc_fname')
        basedir = gpaths['TCWWW']
    else:
        fname_func = get_filenamer('geoips_fname')
    geotiff_fname = fname_func(area_def,
                               xarray_obj,
                               product_name,
                               coverage=coverage,
                               output_type=output_type,
                               output_type_dir=output_type_dir,
                               product_dir=product_dir,
                               product_subdir=product_subdir,
                               source_dir=source_dir,
                               basedir=basedir)

    return geotiff_fname

