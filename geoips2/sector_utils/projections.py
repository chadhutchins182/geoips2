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

''' Projection information for setting up pyresample area definitions'''

projections_avail = {('aeqd',   'aeqd',   'Azimuthal Equidistant')               :0,
                     ('poly',   'poly',   'Polyconic')                           :0,
                     ('gnom',   'gnom',   'Gnomonic')                            :0,
                     ('moll',   'moll',   'Mollweide')                           :1,
                     ('tmerc',  'tmerc',  'Transverse Mercator')                 :0,
                     ('nplaea', 'laea',   'North-Polar Lambert Azimuthal')       :4,
                     ('gall',   'gall',   'Gall Stereographic Cylindrical')      :0,
                     ('mill',   'mill',   'Miller Cylindrical')                  :0,
                     ('merc',   'merc',   'Mercator')                            :0,
                     ('stere',  'stere',  'Stereographic')                       :0,
                     ('npstere','stere',  'North-Polar Stereographic')           :4,
                     ('hammer', 'hammer', 'Hammer')                              :1,
                     ('geos',   'geos',   'Geostationary')                       :2,
                     ('nsper',  'nsper',  'Near-Sided Perspective')              :2,
                     ('vandg',  'vandg',  'van der Grinten')                     :0,
                     ('laea',   'laea',   'Lambert Azimuthal Equal Area')        :0,
                     ('mbtfpq', 'mbtfpq', 'McBryde-Thomas Flat-Polar Quartic')   :1,
                     ('sinu',   'sinu',   'Sinusoidal')                          :1,
                     ('spstere','stere',  'South-Polar Stereographic')           :4,
# lcc does not geolocate correctly
                     ('lcc',    'lcc',    'Lambert Conformal')                   :0,
                     ('npaeqd', 'npaeqd', 'North-Polar Azimuthal Equidistant')   :4,
                     ('ease_sh','ease_sh','Antarctic EASE Grid')                 :4,
                     ('ease_nh','ease_nh','Arctic EASE grid')                    :4,
                     ('eqdc',   'eqdc',   'Equidistant Conic')                   :0,
                     ('cyl',    'eqc',    'Equidistant Cylindrical')             :2,
                     ('eqc',    'eqc',    'Equidistant Cylindrical')             :2,
                     ('omerc',  'omerc',  'Oblique Mercator')                    :0,
# aea does not geolocate correctly
                     ('aea',    'aea',    'Albers Equal Area')                   :0,
                     ('spaeqd', 'spaeqd', 'South-Polar Azimuthal Equidistant')   :4,
                     ('ortho',  'ortho',  'Orthographic')                        :3,
                     ('cass',   'cass',   'Cassini-Soldner')                     :0,
                     ('splaea', 'laea',   'South-Polar Lambert Azimuthal')       :4,
                     ('robin',  'robin',  'Robinson')                            :1,
                    }


def get_projection(name):
    '''Get a dictionary of projection names containing the following keys:
        name:       the basemap projection short name
        p4name:     the Proj4 projection name
        longname:   a long name describing the projection
        type:       an integer indicating how the projection must be set up
    The type field tells the program which arguments will be useful to a given projection
    0) Can use corner lats and lons or center lats and lons with width and height
    1) Ignores corner lats and lons and width/height arguments.  Uses center lat/lon
    2) Can use corner lats and lons or corner coordinates in the local projection
       space, but ignores all other location parameters.
    See http://matplotlib.sourceforge.net/basemap/doc/html/api/basemap_api.html'''
    proj_info = None
    for key, val in projections_avail.items():
        try:
            lowercase_name = name.text.lower()
        except AttributeError:
            lowercase_name = name.lower()
        if lowercase_name == key[0].lower():
            proj_info = {'name': key[0],
                         'p4name': key[1],
                         'longname': key[2],
                         'type': val
                        }
            break
    if proj_info is None:
        raise SectorFileError('%s projection is not defined in basemap.' % name)
    if proj_info['p4name'] is None:
        raise SectorFileError('%s projection is not defined in Proj4.' % name)
    return proj_info
