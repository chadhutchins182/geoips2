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

'''Utilities for merging granules from potentially different data sources / sensors / platforms into a single merge
'''
# Python Standard Libraries
import logging
from datetime import timedelta

# Third Party Installed Libraries

LOG = logging.getLogger(__name__)


def minrange(start_date, end_date):
    '''Check one min at a time'''
    #log.info('in minrange')
    tr = end_date - start_date
    mins = int((tr.seconds + tr.days * 86400 ) / 60)
    LOG.info('%s', mins)
    for n in range(mins):
        yield start_date + timedelta(seconds = (n*60))


def daterange(start_date, end_date):
    '''Check one day at a time. 
        If end_date - start_date is between 1 and 2, days will be 1,
        and range(1) is 0. So add 2 to days to set range'''
    #log.info('in minrange')
    tr = end_date - start_date
    for n in range(tr.days + 2):
        yield start_date + timedelta(n)


def hourrange(start_date, end_date):
    '''Check one hour at a time. '''
    LOG.info('in hourrange')
    tr = end_date - start_date
    for n in range(tr.days*24 + tr.seconds / 3600 ):
        yield start_date + timedelta(seconds = (n*3600))


def find_datafiles_in_range(sector_name, platform_name, source_name, min_time, max_time,
                            basedir, product_name, every_min=True, verbose=False, time_format='%H%M',
                            actual_datetime=None, single_match=False):
    LOG.info('Finding %s %s %s files between %s and %s', sector_name, platform_name, source_name, min_time, max_time)
    from os.path import exists
    from glob import glob
    from geoips2.filenames.product_filenames import netcdf_write_filename
    fnames = []
    first = True
    min_timediff = 10000000
    if (min_time - max_time) < timedelta(minutes=30) or every_min == True:
        for sdt in minrange(min_time, max_time):
            ncdf_fname = netcdf_write_filename(basedir,
                                               product_name=product_name,
                                               source_name=source_name,
                                               platform_name=platform_name,
                                               sector_name=sector_name,
                                               product_datetime=sdt,
                                               time_format=time_format)
            ncdf_fnames = glob(ncdf_fname)
            if first:
                LOG.info('First path: %s', ncdf_fname)
                first = False
            if verbose:
                LOG.info('Checking %s', ncdf_fname)
            if ncdf_fnames:
                if single_match is True and abs((sdt - actual_datetime).seconds) < min_timediff:
                    min_timediff = (sdt - actual_datetime).seconds
                    LOG.info('    Adding %s, min_timediff now %s', ncdf_fnames, min_timediff)
                    fnames = ncdf_fnames
                if single_match is not True:
                    LOG.info('    Adding %s', ncdf_fnames)
                    fnames += ncdf_fnames
                
    return fnames


def get_matching_files(primary_sector_name, subsector_names, platforms, sources, max_time_diffs,
                       basedir, merge_datetime, product_name, time_format='%H%M', buffer_mins=30,
                       verbose=False, single_match=False):
    '''Given the current primary sector, and associated subsectors/platforms/sources, find all matching files
    Parameters:
        primary_sector_name (str): The final sector that all data will be stitched into
                                   ie 'GlobalGlobal'
        subsector_names (list of str): List of all subsectors that will be merged into the final sector (potentially
                                       including the full primary_sector_name.)
                                       ie ['GlobalGlobal', 'GlobalAntarctic', 'GlobalArctic']
        platforms (list of str): List of all desired platforms - platforms, sources, and max_time_diffs correspond to
                                 one another and should be the same length, in the same order.  
        sources (list of str): List of all desired sources - platforms, sources, and max_time_diffs correspond to
                               one another and should be the same length, in the same order.  
        max_time_diffs (list of int): Minutes. List of allowed time diffs for given platform/source. Matches
                                      max_time_diff before the requested merge_datetime argument - platforms, sources,
                                      and max_time_diffs correspond to one another and should be the same length,
                                      in the same order.  
        basedir (str): Base directory in which to look for the matching files
        merge_datetime (datetime.datetime): Attempt matching max_time_diff prior to merge_datetime
        product_name (str): product_name string found in matching files
        time_format (str): Requested time format for filenames (strptime format string)

    Returns: (list of str) List of file names that matched requested paramters.
    '''
                      

    from geoips2.filenames.base_paths import PATHS as gpaths
    from datetime import timedelta

    # MLS1 prev_files should be a dictionary with primary sector names as keys - otherwise it will not work.
    prev_files = []
    actual_datetime = None
    if single_match is True:
        actual_datetime = merge_datetime

    # Go through the list of platforms / sources / allowed time diffs to find the appropriate files for each 
    # data type
    for platform, source, time_diff in zip(platforms,
                                           sources,
                                           max_time_diffs):

        # Go through the list of all subsectors needed to merge into the primary sector listed above
        for currsectname in subsector_names:

            # Get the sector name from the current subsector.
            LOG.info('Checking %s %s %s %s', currsectname, platform, source, time_diff)
            curr_verbose=verbose
            # if platform == 'npp':
            #     curr_verbose=False

            # Use the time/source/platform/sector name to find the desired matching files.
            # MLS1 This should be prev_files[primary_sector_name]
            prev_files += find_datafiles_in_range(currsectname,
                                                  platform,
                                                  source,
                                                  merge_datetime - timedelta(minutes=time_diff),
                                                  merge_datetime + timedelta(minutes=buffer_mins),
                                                  basedir=basedir,
                                                  product_name=product_name,
                                                  every_min=True,
                                                  verbose=curr_verbose,
                                                  time_format=time_format,
                                                  actual_datetime=actual_datetime,
                                                  single_match=single_match)
    return prev_files
