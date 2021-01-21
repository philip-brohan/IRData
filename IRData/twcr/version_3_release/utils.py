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

def _get_data_dir(version="3"):
    """Return the root directory containing 20CR netCDF files"""
    g = "%s/20CR/version_%s/" % (os.environ["SCRATCH"], version)
    return g


def _get_data_file_name(variable, year, month=None, version="3", member=1):
    """Return the name of the file containing data for the
    requested variable, at the specified time, from the
    20CR version."""
    base_dir = _get_data_dir(version=version)
    # If monthly file exists, use that, otherwise, annual file
    if month is not None:
        name = "%s/%04d/%s.%04d%02d_mem%03d.nc" % (
            base_dir,
            year,
            variable,
            year,
            month,
            member,
        )
    if month is None or not os.path.isfile(name):
        name = "%s/%04d/%s.%04d_mem%03d.nc" % (
            base_dir,
            year,
            variable,
            year,
            member,
        )
    return name
