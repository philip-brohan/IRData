# (C) British Crown Copyright 2017, Met Office
#
# This code is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#

# Utility functions for version 3-final

import os

# Supported analysis variables
monolevel_analysis=('PRMSL','TMP2m','UGRD10m','VGRD10m','PRATE')

def _get_data_dir():
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_3/" % os.environ['SCRATCH']
    return g

def _get_data_file_name(variable,year,member=1):
    """Return the name of the file containing data for the
       requested variable, at the specified time, from the
       20CR version."""
    base_dir=_get_data_dir()
    if (variable in monolevel_analysis):
        name="%s/%04d/%s.%04d_mem%03d.nc" % (base_dir,year,variable,
                                             year,member)
    else:
        raise ValueError('Unsupported variable: %s' % variable)
    return name

