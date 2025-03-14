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

Documentation and Style Strategy
===========================================

GeoIPS 2.0 uses Sphinx with the Napoleon extension for automated documentation generation.

https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

The **geoips2/docs** directory contains high level restructured text (rst) format documentation (including this page),
along with a **build_docs.sh** script that will setup sphinx and build complete documentation from the high level rst
files as well as docstrings contained within the GeoIPS 2.0 source code.


GeoIPS 2.0 Syntax and Style Checking
------------------------------------

GeoIPS 2.0 uses the Google Style Guide, including Google style docstrings within the code base for simplicity:

https://google.github.io/styleguide/pyguide.html

bandit, flake8, and pylint are used to enforce appropriate style, security, and syntax usage.

The installation script called from **geoips2/README.md** contains steps for setting up VIM8 with
automated syntax checking and highlighting (including automated flake8, pylint, and bandit error / warning
highlighting), to help enforce desired style guides.
