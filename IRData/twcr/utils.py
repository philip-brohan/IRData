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

# Utility functions for file and variable name mapping for 20CR.

from . import version_2c
from . import version_3
from . import version_3_release

# File name for data for a given variable and month
def _hourly_get_file_name(variable,year,month=6,
                          day=15,hour=12,
                          member=None,
                          version=None,type=None):
    if vn=='2c':
        return version_2c._get_data_file_name(
                                 variable,year,type=type)
    if vn=='3' or vn[0]=='4' or vn[0]=='0':
        return version_3_release._get_data_file_name(
                                 variable,year,month,member=member)
       
    raise Exception('Invalid version %s' % version)
