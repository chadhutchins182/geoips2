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

import logging

LOG = logging.getLogger(__name__)


def remove_duplicates(fnames, filename_format, remove_files=False):
    removed_files = []
    saved_files = []
    from geoips2.sector_utils.utils import is_sector_type
    from geoips2.dev.filename import get_filenamer
    from importlib import import_module
    fnamer = get_filenamer(filename_format)
    if hasattr(import_module(fnamer.__module__), f'{filename_format}_remove_duplicates'):
        fnamer_remove_dups = getattr(import_module(fnamer.__module__), f'{filename_format}_remove_duplicates')
        for fname in fnames:
            curr_removed_files, curr_saved_files = fnamer_remove_dups(fname, remove_files=remove_files)
            removed_files += curr_removed_files
            saved_files += curr_saved_files
    else:
        LOG.warning(f'SKIPPING DUPLICATE REMOVAL no {filename_format}_remove_duplicates defined')

    return removed_files, saved_files


