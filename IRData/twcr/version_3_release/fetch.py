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

# Fetch 20CR V3 data from NERSC and store it on $SCRATCH.

import os
import sys
import subprocess
import datetime
import tarfile

from .utils import _get_data_file_name
from .utils import _get_data_dir


def _get_remote_file_name(variable, year):
    """Get all data for one variable, for one year, from 20CR archive at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        year (:obj:`int`): Year to get data for.

    Will retrieve the data for the year of the given date-time. If the selected time is very close to the end of the calendar year, loading data for that time will also need data from the next calendar year (for interpolation). In this case, also fetch the data for the next calendar year.

    Raises:
        StandardError: If variable is not a supported value.

    |
    """

    remote_dir = (
        "https://portal.nersc.gov/archive/home/projects/incite11/www/"
        + "20C_Reanalysis_version_3/everymember_anal_netcdf/subdaily"
    )

    if variable == "observations":
        remote_file = (
            "http://portal.nersc.gov/m958/v3_observations/" + "%04d.zip"
        ) % year
        return remote_file

    remote_file = "%s/%s/%s_%04d.tar" % (remote_dir, variable, variable, year)
    return remote_file


def _get_tar_file_name(variable, year):
    return "%s/%s_%04d.tar" % (_get_data_dir(), variable, year)


def _unpack_downloaded(variable, year):
    local_file = _get_tar_file_name(variable, year)
    tar = tarfile.open(local_file, "r")
    local_dir = os.path.dirname(local_file)
    tar.extractall(path=local_dir)
    tar.close()
    # Update the extracted file times
    #  To stop SCRATCH deleting them as too old
    nfiles = os.listdir("%s/%04d" % (local_dir, year))
    for nfile in nfiles:
        os.utime("%s/%04d/%s" % (local_dir, year, nfile))
    # os.remove(local_file)


def fetch(variable, dtime):

    ndtime = dtime + datetime.timedelta(hours=6)
    if ndtime.year != dtime.year:
        fetch(variable, ndtime)

    local_file = _get_data_file_name(variable, dtime.year)

    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file = _get_remote_file_name(variable, dtime.year)

    # Download the tar file
    cmd = "wget -O %s %s" % (_get_tar_file_name(variable, dtime.year), remote_file)
    wg_retvalue = subprocess.call(cmd, shell=True)
    if wg_retvalue != 0:
        raise Exception("Failed to retrieve data")
    _unpack_downloaded(variable, dtime.year)
