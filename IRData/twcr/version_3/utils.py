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

# Utility functions for version 3-preliminary

import os

# Supported analysis variables
monolevel_analysis = (
    "prmsl",
    "air.2m",
    "uwnd.10m",
    "vwnd.10m",
    "icec",
    "sst",
    "air.sfc",
)
multilevel_analysis = ("tmp", "uwnd", "vwnd", "hgt", "spfh", "pvort")
# Suported forecast variables
monolevel_forecast = "prate"


def _get_data_dir(version="4.5.1"):
    """Return the root directory containing 20CR netCDF files"""
    g = "%s/20CR/version_%s/" % (os.environ["SCRATCH"], version)
    return g


def _get_data_file_name(
    variable, year, month, height=None, level=None, ilevel=None, version="4.5.1"
):
    """Return the name of the file containing data for the
    requested variable, at the specified time, from the
    20CR version."""
    base_dir = _get_data_dir(version)
    if variable in monolevel_analysis or variable in monolevel_forecast:
        name = "%s/%04d/%02d/%s.nc" % (base_dir, year, month, variable)
    elif variable in multilevel_analysis:
        if level is not None:
            name = "%s/%04d/%02d/%s.%dmb.nc" % (base_dir, year, month, variable, level)
        elif ilevel is not None:
            name = "%s/%04d/%02d/%s.%dK.nc" % (base_dir, year, month, variable, ilevel)
        elif height is not None:
            name = "%s/%04d/%02d/%s.%dm.nc" % (base_dir, year, month, variable, height)
        else:
            raise ValueError("No height, level, or ilevel specified for 3d variable")
    else:
        raise ValueError("Unsupported variable: %s" & variable)
    return name
