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
    ''' Script to test all dev and stable interfaces'''

    interfaces = ['stable.reader',
                  'dev.alg',
                  'dev.boundaries',
                  'dev.cmap',
                  'dev.filename',
                  'dev.gridlines',
                  'dev.interp',
                  'dev.output',
                  'dev.procflow',
                  'dev.product']

    for curr_interface in interfaces:
        interface_name = curr_interface.split('.')[1]
        print('')
        print(f'Testing {curr_interface}...')
        print('ipython')
        print(f'    from geoips2.{curr_interface} import test_{interface_name}_interface')
        print(f'    test_{interface_name}_interface()')
        test_curr_interface = getattr(import_module(f'geoips2.{curr_interface}'),
                                      f'test_{interface_name}_interface')
        try:
            out_dict = test_curr_interface()
        except Exception:
            print(traceback.format_exc())
            raise

        print(f'SUCCESSFUL INTERFACE {curr_interface}')

        ppprinter = pprint.PrettyPrinter(indent=2)
        ppprinter.pprint(out_dict)

        for modname in out_dict['validity_check']:
            if not out_dict['validity_check'][modname]:
                print(f'FAILED INTERFACE {curr_interface} on {modname}')
                raise TypeError(f'Failed validity check on {modname} in interface {curr_interface}')


if __name__ == '__main__':
    main()
