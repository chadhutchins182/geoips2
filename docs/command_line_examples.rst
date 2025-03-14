 | # # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
 | # # # 
 | # # # Author:
 | # # # Naval Research Laboratory, Marine Meteorology Division
 | # # # 
 | # # # This program is free software: you can redistribute it and/or modify it under
 | # # # the terms of the NRLMMD License included with this program.  If you did not
 | # # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
 | # # # information.
 | # # # 
 | # # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
 | # # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 | # # # included license for more details.

Example Command Line Calls
==========================

The standard installation steps include download of sample ABI test datasets from the public NOAA AWS
repository.  These sample commands use the pre-downloaded ABI data.


Geostationary Infrared annotated imagery over static sector
-----------------------------------------------------------

Plot ABI Infrared product over static sector, including:
    * annotated png using cartopy and matplotlib

Note the first time processing ABI or AHI data can take several minutes, as it is pre-generating geolocation files
over the given sector to cache for use in subsequent runs.

.. code-block:: bash
    :linenos:

    # For reference
    # --procflow single_source            DEFINED: geoips2/interface_modules/procflows/single_source.py
    # --readername abi_netcdf             DEFINED: geoips2/interface_modules/readers/abi_netcdf.py
    # --output_format imagery_annotated   DEFINED: geoips2/interface_modules/output_formats/imagery_annotated.py
    # --filename_format geoips_fname      DEFINED: geoips2/interface_modules/filename_formats/geoips_fname.py
    # --product_name Infrared             DEFINED: geoips2/yaml_configs/product_params/visir/Infrared.yaml

    run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
              --procflow single_source \
              --reader_name abi_netcdf \
              --product_name Infrared \
              --output_format imagery_annotated \
              --filename_format geoips_fname \
              --sector_list goes16 \
              --sectorfiles $GEOIPS2/tests/sectors/goes16.yaml

.. image:: images/20200918.195020.goes-16.abi.Infrared.goes16.45p56.noaa.10p0.png
   :width: 600


Geostationary Visible netCDF output
-----------------------------------

Create ABI Visible netcdf output, over a TC sector

.. code-block:: bash
    :linenos:

    # For reference
    # --trackfile_parser bdeck_parser     DEFINED: geoips2/interface_modules/trackfile_parsers/bdeck_parser.py

    run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
              --procflow single_source \
              --reader_name abi_netcdf \
              --product_name Visible \
              --output_format netcdf_geoips \
              --filename_format geoips_netcdf_fname \
              --tc_template_yaml $GEOIPS2/geoips2/yaml_configs/sectors_dynamic/tc_web_2km_template.yaml \
              --trackfiles $GEOIPS2/tests/sectors/bal202020.dat \
              --trackfile_parser bdeck_parser

.. include:: yaml/20200918.195020.goes-16.Visible_latitude_longitude.tc2020al20teddy.nc.yaml
   :literal:


Geostationary IR-BD imagery over TC specific sector
---------------------------------------------------

Plot the ABI IR-BD product over TC2020 AL20 Teddy, with
    * annotated png using cartopy and matplotlib
    * associated metadata YAML files

.. code-block:: bash
    :linenos:

    # For reference
    # --boundaries_params tc_visir        DEFINED: geoips2/yaml_configs/plotting_params/boundaries/tc_visir.yaml
    # --gridlines_params tc_visir         DEFINED: geoips2/yaml_configs/plotting_params/gridlines/tc_visir.yaml

    run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
              --procflow single_source \
              --reader_name abi_netcdf \
              --product_name IR-BD \
              --output_format imagery_annotated \
              --filename_format tc_fname \
              --gridlines_params tc_pmw \
              --boundaries_params tc_pmw \
              --trackfiles $GEOIPS2/tests/sectors/bal202020.dat \
              --trackfile_parser bdeck_parser

.. image:: images/20200918_195020_AL202020_abi_goes-16_IR-BD_110kts_100p00_1p0.png
   :width: 600

.. include:: yaml/20200918_195020_AL202020_abi_goes-16_IR-BD_110kts_100p00_1p0.png.yaml
   :literal:


Geostationary WV product over TC specific sector
------------------------------------------------

Plot the ABI WV product over TC2020 AL20 Teddy, with
    * "clean" png with no coast lines, borders, gridlines, or title information,
    * associated metadata YAML files

.. code-block:: bash
    :linenos:

    run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
              --procflow single_source \
              --reader_name abi_netcdf \
              --product_name WV \
              --output_format imagery_clean \
              --filename_format tc_fname \
              --trackfiles $GEOIPS2/tests/sectors/bal202020.dat \
              --trackfile_parser bdeck_parser

.. image:: images/20200918_195020_AL202020_abi_goes-16_WV_110kts_100p00_1p0.png
   :width: 600

.. include:: yaml/20200918_195020_AL202020_abi_goes-16_WV_110kts_100p00_1p0.png.yaml
   :literal:


Config based processing for ABI dataset
---------------------------------------

Efficiently plot ABI annotated imagery over both a static and TC sector with a single call.
    * static Infrared output
    * TC Infrared-Gray, IR-BD, Visible, and WV annotated imagery and YAML metadata outputs

.. code-block:: bash
    :linenos:

    run_procflow --output_config $GEOIPS2/tests/yaml_configs/abi_test.yaml \
                 --procflow config_based

.. include:: yaml/abi_test.yaml
   :literal:
