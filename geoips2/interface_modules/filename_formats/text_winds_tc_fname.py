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

''' Specifications for output filename formats for tc product types. '''

import logging

from os.path import join as pathjoin, splitext as pathsplitext
from os.path import dirname as pathdirname, basename as pathbasename
from datetime import datetime, timedelta
from glob import glob
from os import unlink as osunlink

from geoips2.filenames.base_paths import PATHS as gpaths
from geoips2.data_manipulations.merge import minrange

filename_type = 'xarray_metadata_to_filename'

LOG = logging.getLogger(__name__)


def text_winds_tc_fname(xarray_obj, extension='.txt', basedir=gpaths['TCWWW']):
    area_def = xarray_obj.area_definition
    return assemble_windspeeds_text_tc_fname(basedir=basedir,
                                             tc_area_id=area_def.area_id,
                                             tc_year=int(area_def.sector_info['storm_year']),
                                             tc_basin=area_def.sector_info['storm_basin'],
                                             tc_stormnum=int(area_def.sector_info['storm_num']),
                                             source_name=xarray_obj.source_name,
                                             platform_name=xarray_obj.platform_name,
                                             product_datetime=xarray_obj.start_datetime,
                                             data_provider=xarray_obj.data_provider,
                                             extension=extension)


def assemble_windspeeds_text_tc_fname(basedir, tc_area_id, tc_year, tc_basin, tc_stormnum, source_name,
                                      platform_name, product_datetime, data_provider, extension='.txt'):
    ''' Produce full output product path from product / sensor specifications.

        Args:
            basedir (str) :  base directory
            tc_year (int) :  Full 4 digit storm year
            tc_basin (str) :  2 character basin designation
                                   SH Southern Hemisphere
                                   WP West Pacific
                                   EP East Pacific
                                   CP Central Pacific
                                   IO Indian Ocean
                                   AL Atlantic
            tc_stormnum (int) : 2 digit storm number
                                   90 through 99 for invests
                                   01 through 69 for named storms
            platform_name (str) : Name of platform (satellite)
            product_datetime (datetime) : Start time of data used to generate product

        Returns:
            str: to full path of output filename of the format:
              <basedir>/tc<tc_year>/<tc_basin>/<tc_basin><tc_stormnum><tc_year>/txt/
              <source_name>_<platform_name>_surface_winds_<data_provider>_<YYYYMMDDHHMN>

        Usage:
            >>> startdt = datetime.strptime('20200216T001412', '%Y%m%dT%H%M%S')
            >>> assemble_windspeeds_text_tc_fname('/outdir', 2020, 'SH', 16, 'smap-spd', 'smap', startdt, 'remss')
            '/outdir/tc2020/SH/SH162020/txt/
    '''

    from geoips2.interface_modules.filename_formats.utils.tc_file_naming import tc_storm_basedir
    path = pathjoin(tc_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    'txt')
    fname = '_'.join([source_name,
                      'surface_winds',
                      data_provider,
                      platform_name,
                      tc_area_id,
                      product_datetime.strftime('%Y%m%d%H%M')])
    if extension is not None:
        fname = f'{fname}{extension}'
    return pathjoin(path, fname)
