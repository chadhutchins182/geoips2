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

'''Simple test script to run "test_<interface>_interface" for each dev and stable interface'''

import pprint
from importlib import import_module
import traceback


def main():
    ''' Script to list all modules available in the current geoips2 instantiation '''

    interfaces = {'stable.reader': 'list_readers_by_type',
                  'dev.alg': 'list_algs_by_type',
                  'dev.boundaries': 'list_boundaries_by_type',
                  'dev.cmap': 'list_cmaps_by_type',
                  'dev.filename': 'list_filenamers_by_type',
                  'dev.gridlines': 'list_gridlines_by_type',
                  'dev.interp': 'list_interps_by_type',
                  'dev.output': 'list_outputters_by_type',
                  'dev.procflow': 'list_procflows_by_type',
                  'dev.product': 'list_products_by_type'}

    for curr_interface, list_func in interfaces.items():
        print('')
        test_curr_interface = getattr(import_module(f'geoips2.{curr_interface}'),
                                      f'{list_func}')
        try:
            out_dict = test_curr_interface()
        except Exception:
            print(traceback.format_exc())
            raise

        print(f'Available {curr_interface} modules:')

        ppprinter = pprint.PrettyPrinter(indent=2)
        ppprinter.pprint(out_dict)


if __name__ == '__main__':
    main()
