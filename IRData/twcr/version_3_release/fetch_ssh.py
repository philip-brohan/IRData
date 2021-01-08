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
import glob
import shutil

from .utils import _get_data_file_name
from .utils import _get_data_dir


def _get_remote_file_name_ssh(variable, year, month, version, user="pbrohan"):

    remote_dir = (
        "%s@dtn02.nersc.gov:/global/cscratch1/sd/%s/"
        + "20CRv3.working.nc/version_%1s%1s%1s"
    ) % (user, user, version[0], version[2], version[4])

    if variable == "observations":
        remote_file = "%s/%04d/%02d/%04d%02d_psobs.tar" % (
            remote_dir,
            year,
            month,
            year,
            month,
        )
        return remote_file

    remote_file = "%s/%04d/%02d/%s_%04d%02d_v3_x%1s%1s%1s.tar" % (
        remote_dir,
        year,
        month,
        variable,
        year,
        month,
        version[0],
        version[2],
        version[4],
    )
    return remote_file


def _get_tar_file_name_ssh(variable, year, month, version):
    if variable == "observations":
        return "%s/%04d%02d_psobs.tar" % (_get_data_dir(version), year, month)
    return "%s/%s_%04d%02d.tar" % (_get_data_dir(version), variable, year, month)


def _unpack_downloaded_ssh(variable, year, month, version):
    local_file = _get_tar_file_name_ssh(variable, year, month, version)
    tar = tarfile.open(local_file, "r")
    local_dir = os.path.dirname(local_file)
    tar.extractall(path=local_dir)
    tar.close()
    if variable == "observations":
        otdir = "%s/observations/%04d" % (local_dir, year)
        if not os.path.exists(otdir):
            os.makedirs(otdir)
        odirs = glob.glob("%s/%04d%02d????" % (local_dir, year, month))
        for od in odirs:
            m = shutil.move(od, otdir)
        for root, dirs, files in os.walk(otdir):
            for file in files:
                os.utime(os.path.join(root, file))
    else:
        # Update the extracted file times
        #  To stop SCRATCH deleting them as too old
        nfiles = os.listdir("%s/%04d" % (local_dir, year))
        for nfile in nfiles:
            os.utime("%s/%04d/%s" % (local_dir, year, nfile))
    # os.remove(local_file)


def fetch_ssh(variable, dtime, version, user="pbrohan"):

    ndtime = dtime + datetime.timedelta(hours=6)
    if ndtime.month != dtime.month:
        fetch_ssh(variable, ndtime)

    local_file = _get_tar_file_name_ssh(variable, dtime.year, dtime.month, version)

    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file = _get_remote_file_name_ssh(
        variable, dtime.year, dtime.month, version, user=user
    )

    # Download the tar file
    cmd = "scp %s %s" % (remote_file, local_file)
    scp_retvalue = subprocess.call(cmd, shell=True)
    if scp_retvalue != 0:
        raise Exception("Failed to retrieve data. Code: %d" % scp_retvalue)
    _unpack_downloaded_ssh(variable, dtime.year, dtime.month, version)
