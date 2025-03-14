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

'''Modules to access TC tracks, based on locations found in the deck files.  These are duplicated from
    geoips.sectorfile.dynamic to avoid using modules from geoips. set_tc_sector still imports from sectorfile,
    as we are still internally relying on the Sector objects. '''
import os
from datetime import datetime
import logging

from geoips2.filenames.base_paths import PATHS as gpaths

LOG = logging.getLogger(__name__)

# If we ever revert back to numbered storm from named storm, we may need to include this list in "get_final_storm_name"
# rather than just INVEST
# UNNAMED_STORM_NAMES = ['invest', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
#                        'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
#                        'nineteen', 'twenty', 'twenty-one']


def tc_fname_metadata(area_def, xarray_obj, product_filename,
                      metadata_dir='metadata', metadata_type='sector_information'):

    allowed_metadata_types = ['sector_information', 'archer_information', 'storm_information']

    if metadata_type not in allowed_metadata_types:
        raise TypeError('Unknown metadata type {0}, allowed {1}'.format(metadata_type, allowed_metadata_types))

    basedir = gpaths['TCWWW']
    tc_year = int(area_def.sector_info['storm_year'])
    tc_basin = area_def.sector_info['storm_basin']
    tc_stormnum = int(area_def.sector_info['storm_num'])
    metadata_type = 'sector_information'
    metadata_datetime = xarray_obj.start_datetime
    metadata_dir = metadata_dir

    from os.path import join as pathjoin
    from os.path import basename
    from geoips2.interface_modules.filename_formats.utils.tc_file_naming import tc_storm_basedir
    metadata_yaml_dirname = pathjoin(tc_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                                     metadata_dir,
                                     metadata_type,
                                     metadata_datetime.strftime('%Y%m%d'))
    metadata_yaml_basename = basename(product_filename)+'.yaml'

    return pathjoin(metadata_yaml_dirname, metadata_yaml_basename)


def produce_sector_metadata(area_def, xarray_obj, product_filename, metadata_dir='metadata'):
    ''' Produce metadata yaml file of sector information associated with the final_product
    Args:
        area_def (AreaDefinition) : Pyresample AreaDefintion object
        final_product (str) : Product that is associated with the passed area_def
        metadata_dir (str) : DEFAULT 'metadata' Subdirectory name for metadata (using non-default allows for
                                                non-operational outputs)

    Returns:
        (str) : Metadata yaml filename, if one was produced.
    '''
    from geoips2.interface_modules.output_formats.utils.metadata import output_metadata_yaml

    metadata_yaml_filename = tc_fname_metadata(area_def, xarray_obj, product_filename, metadata_dir,
                                               metadata_type='sector_information')
    # os.path.join does not take a list, so "*" it
    # product_partial_path = product_filename.replace(gpaths['TCWWW'], 'https://www.nrlmry.navy.mil/tcdat')
    from geoips2.dev.utils import replace_geoips_paths
    product_partial_path = replace_geoips_paths(product_filename)
    # product_partial_path = pathjoin(*final_product.split('/')[-5:-1]+[basename(final_product)])
    return output_metadata_yaml(metadata_yaml_filename, area_def, xarray_obj, product_partial_path)


def create_tc_sector_info_dict(clat, clon, synoptic_time, storm_year, storm_basin, storm_num, aid_type=None,
                               storm_name=None, final_storm_name=None,
                               deck_line=None, source_sector_file=None,
                               pressure=None, vmax=None):
    ''' Create storm info dictionary from items

    Args:
        clat (float) : center latitude of storm
        clon (float) : center longitude of storm
        synoptic_time (datetime) : time of storm location
        storm_year (int) : 4 digit year of storm
        storm_basin (str) : 2 digit basin identifier
        storm_num (int) : 2 digit storm number
        storm_name (str) : Common name of storm
        deck_line (str) :  source deck line for storm information
        pressure (float) : minimum pressure
        vmax (float) : maximum wind speed
    '''
    fields = {}
    fields['clat'] = clat
    fields['clon'] = clon
    fields['synoptic_time'] = synoptic_time
    fields['storm_year'] = storm_year
    fields['storm_basin'] = storm_basin
    fields['storm_num'] = int(storm_num)
    fields['storm_name'] = 'unknown'
    fields['aid_type'] = 'unknown'
    fields['final_storm_name'] = 'unknown'
    fields['source_sector_file'] = 'unknown'
    if aid_type:
        fields['aid_type'] = aid_type
    if storm_name:
        fields['storm_name'] = storm_name
    if final_storm_name:
        LOG.info('USING passed final_storm_name %s', final_storm_name)
        fields['final_storm_name'] = final_storm_name
    else:
        LOG.info('USING storm_name as final_storm_name %s', storm_name)
        fields['final_storm_name'] = storm_name
    if source_sector_file:
        from geoips2.dev.utils import replace_geoips_paths
        fields['source_sector_file'] = replace_geoips_paths(source_sector_file)
    fields['pressure'] = pressure
    fields['deck_line'] = deck_line
    fields['vmax'] = vmax
    fields['source_filename'] = fields['source_sector_file']
    fields['parser_name'] = None
    return fields


def get_tc_area_id(fields, finalstormname, tcyear):
    if not finalstormname:
        finalstormname = fields['storm_name']
    newname = '{0}{1:02d}{2}'.format(fields['storm_basin'].lower(),
                                 int(fields['storm_num']),
                                 finalstormname.lower())

    newname = newname.replace('_', '').replace('.', '').replace('-', '')

    # This ends up being tc2016io01one
    area_id = 'tc'+str(tcyear)+newname
    return area_id


def get_tc_long_description(area_id, fields):
    if 'interpolated_time' in fields:
        long_description = '{0} interpolated_time {1}'.format(area_id, str(fields['interpolated_time']))
    else:
        long_description = '{0} synoptic_time {1}'.format(area_id, str(fields['synoptic_time']))
    return long_description


def set_tc_area_def(fields, tcyear=None,
                    finalstormname=None, source_sector_file=None,
                    clat=None, clon=None,
                    template_yaml=gpaths['TC_TEMPLATE'],
                    aid_type=None):
    ''' Set the TC area definition, using specified arguments.

    Args:
        fields (dict) : Dictionary of TC sector_info fields (clat, clon, storm name, etc)
                            Valid fields can be found in geoips2.sector_utils.utils.SECTOR_INFO_ATTRS
        tcyear (int) : DEFAULT None, Passed tcyear - since current year may not match tcyear for SHEM storms
        finalstormname (str) : DEFAULT None, finalstormname allows reprocessed storms to go in final storm directory
        source_sector_file (str) : DEFAULT None, attach source_sector_file to area_definition if known
        clat (float) : DEFAULT None, specify clat/clon separately from that found in 'fields'
        clon (float) : DEFAULT None, specify clat/clon separately from that found in 'fields'
        template_yaml (str) : DEFAULT gpaths['TC_TEMPLATE']
                                      Path to template YAML file to use when setting up area definition.
        aid_type (str) : DEFAULT None, type of TC aid (BEST, MBAM, etc)
    Returns:
        (AreaDefinition) : List of pyresample AreaDefinition objects

    '''

    import yaml
    if template_yaml is None:
        template_yaml = gpaths['TC_TEMPLATE']
    with open(template_yaml, 'r') as fobj:
        template_dict = yaml.safe_load(fobj)
    template_func_name = template_dict['area_def_generator_func']
    template_args = template_dict['area_def_generator_args']

    if not finalstormname and 'final_storm_name' in fields:
        finalstormname = fields['final_storm_name']
    if not source_sector_file and 'source_sector_file' in fields:
        source_sector_file = fields['source_sector_file']
    if not source_sector_file and 'source_filename' in fields:
        source_sector_file = fields['source_filename']
    if not tcyear:
        tcyear = fields['storm_year']
    if clat is None:
        clat = fields['clat']
    if clon is None:
        clon = fields['clon']

    area_id = get_tc_area_id(fields, finalstormname, tcyear)
    long_description = get_tc_long_description(area_id, fields)

    from geoips2.geoips2_utils import find_entry_point
    # These are things like 'clat_clon_resolution_shape'
    template_func = find_entry_point('area_def_generators', template_func_name)
    # Probably generalize this at some point. For now I know those are the ones that are <template>
    template_args['area_id'] = area_id
    template_args['long_description'] = long_description
    template_args['clat'] = clat
    template_args['clon'] = clon
    area_def = template_func(**template_args)

    if 'interpolated_time' in fields:
        area_def.sector_start_datetime = fields['interpolated_time']
        area_def.sector_end_datetime = fields['interpolated_time']
    else:
        area_def.sector_start_datetime = fields['synoptic_time']
        area_def.sector_end_datetime = fields['synoptic_time']
    area_def.sector_type = 'tc'
    area_def.sector_info = {}

    # area_def.description is Python3 compatible, and area_def.name is Python2 compatible
    area_def.description = long_description
    if not hasattr(area_def, 'name'):
        area_def.name = long_description

    from geoips2.dev.utils import replace_geoips_paths
    area_def.sector_info['source_sector_file'] = replace_geoips_paths(source_sector_file)
    # area_def.sector_info['sourcetemplate'] = dynamic_templatefname
    # area_def.sector_info['sourcedynamicxmlpath'] = dynamic_xmlpath
    # FNMOC sectorfile doesn't have pressure
    for fieldname in fields.keys():
        area_def.sector_info[fieldname] = fields[fieldname]
    area_def.sector_info['storm_year'] = tcyear

    # If storm_name is undefined in the current deck line, set it to finalstormname
    if area_def.sector_info['storm_name'] == '' and finalstormname:
        LOG.debug('USING finalstormname "%s" rather than deck storm name "%s"',
                  finalstormname,
                  area_def.sector_info['storm_name'])
        area_def.sector_info['storm_name'] = finalstormname
        area_def.sector_info['final_storm_name'] = finalstormname

    LOG.debug('      Current TC sector: %s', fields['deck_line'])
    return area_def


def trackfile_to_area_defs(trackfile_name, trackfile_parser='gdeck_parser', template_yaml=None):
    ''' Get TC area definitions for the specified text trackfile, limit to optionally specified trackfile_sectorlist

    Args:
        trackfile (str) : Full path to trackfile, convert each line into a separate area_def
        trackfile_parser (str) : Parser to use from interface_modules/trackfile_parsers on trackfiles
    Returns:
        (list) : List of pyresample AreaDefinition objects
    '''
    if trackfile_parser is None:
        trackfile_parser = 'gdeck_parser'

    from geoips2.geoips2_utils import find_entry_point
    parser = find_entry_point('trackfile_parsers', trackfile_parser)

    all_fields, final_storm_name, tc_year = parser(trackfile_name)

    area_defs = []
    for fields in all_fields:
        # area_defs += [set_tc_sector(fields, dynamic_templatefname, finalstormname, tcyear, sfname, dynamic_xmlpath)]
        area_defs += [set_tc_area_def(fields, tc_year, finalstormname=final_storm_name,
                                      source_sector_file=trackfile_name, template_yaml=template_yaml)]

    return area_defs


def interpolate_storm_location(interp_dt, longitudes, latitudes, synoptic_times):
    ''' Interpolate the storm location at a specific time based on a list of known locations and times'''
    LOG.info('interp_dt: %s\nlatitudes:\n%s\nlongitudes:\n%s\nsynoptic_times:\n%s',
             interp_dt, latitudes, longitudes, synoptic_times)
    # from IPython import embed as shell; shell()
