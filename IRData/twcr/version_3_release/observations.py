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

# Handle observations for version 3-final

import datetime
import os
import os.path
import subprocess
import zipfile
import pandas
import numpy
import getpass

from .utils import _get_data_dir


def _observations_zip_file(year, version="3"):
    return "%s/observations/%04d.zip" % (_get_data_dir(), year)


def _observations_file_name(year, month, day, hour, version="3"):
    of = "%s/observations/%04d/%04d%02d%02d%02d_psobs_posterior.txt" % (
        _get_data_dir(version),
        year,
        year,
        month,
        day,
        hour,
    )
    if os.path.isfile(of):
        return of
    return "%s.gz" % of


def _observations_remote_file(year):
    remote_file = (
        "http://portal.nersc.gov/project/m958/v3_observations/" + "%04d.zip"
    ) % year
    return remote_file


def fetch_observations(dtime):

    ndtime = dtime + datetime.timedelta(hours=6)
    if ndtime.year != dtime.year:
        fetch_observations(ndtime)
    o_dir = "%s/observations/%04d" % (_get_data_dir(), dtime.year)
    if os.path.exists(o_dir):
        if len(os.listdir(o_dir)) >= 1460:
            return
    _download_observations(dtime.year)
    _unpack_downloaded_observations(dtime.year)


def _download_observations(year):
    remote_file = _observations_remote_file(year)
    local_file = _observations_zip_file(year)
    if os.path.isfile(local_file):
        return
    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))
    cmd = "wget -O %s %s" % (local_file, remote_file)
    wg_retvalue = subprocess.call(cmd, shell=True)
    if wg_retvalue != 0:
        os.remove(local_file)
        raise Exception("Failed to retrieve data")


def _unpack_downloaded_observations(year):
    local_file = _observations_zip_file(year)
    zf = zipfile.ZipFile(local_file)
    zf.extractall("%s/observations/" % _get_data_dir())
    os.remove(local_file)


def load_observations_1file(dtime, version):
    """Retrieve all the observations for an individual assimilation run."""
    of_name = _observations_file_name(
        dtime.year, dtime.month, dtime.day, dtime.hour, version=version
    )
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o = pandas.read_fwf(
        of_name,
        colspecs=[
            (0, 19),
            (20, 50),
            (52, 64),
            (66, 68),
            (69, 72),
            (74, 80),
            (81, 87),
            (88, 95),
            (97, 102),
            (103, 110),
            (111, 112),
            (113, 123),
            (124, 134),
            (135, 145),
            (146, 156),
            (157, 167),
            (168, 175),
            (176, 183),
            (184, 191),
            (192, 200),
            (201, 205),
            (206, 213),
            (214, 221),
            (222, 223),
        ],
        header=None,
        encoding="ISO-8859-1",
        names=[
            "UID",
            "Name",
            "ID",
            "Type",
            "NCEP.Type",
            "Longitude",
            "Latitude",
            "Observed",
            "Time.offset",
            "Observed.2",
            "Skipped",
            "Bias.correction",
            "Obfit.prior",
            "Obfit.post",
            "Obsprd.prior",
            "Obsprd.post",
            "Oberrvar.orig.out",
            "Oberrvar.out",
            "Oberrvar.use",
            "Paoverpb.save",
            "Prob.gross.error",
            "Localization.length.scale",
            "Lnsigl",
            "QC.failure.flag",
        ],
        converters={
            "UID": str,
            "Name": str,
            "ID": str,
            "Type": str,
            "NCEP.Type": int,
            "Longitude": float,
            "Latitude": float,
            "Observed": float,
            "Time.offset": float,
            "Observed.2": float,
            "Skipped": int,
            "Bias.correction": float,
            "Obfit.prior": float,
            "Obfit.post": float,
            "Obsprd.prior": float,
            "Obsprd.post": float,
            "Oberrvar.orig.out": float,
            "Oberrvar.out": float,
            "Oberrvar.use": float,
            "Paoverpb.save": float,
            "Prob.gross.error": float,
            "Localization.length.scale": float,
            "Lnsigl": float,
            "QC.failure.flag": int,
        },
        na_values=[
            "NA",
            "*",
            "***",
            "*****",
            "*******",
            "**********",
            "-99",
            "9999",
            "-999",
            "9999.99",
            "10000.0",
            "-9.99",
            "999999999999",
            "9",
        ],
        comment=None,
        compression="infer",
    )
    return o


def load_observations(start, end, version="3"):
    result = None
    ct = start
    while ct < end:
        if int(ct.hour) % 6 != 0:
            ct = ct + datetime.timedelta(hours=1)
            continue
        o = load_observations_1file(ct, version=version)
        dtm = pandas.to_datetime(o.UID.str.slice(0, 10), format="%Y%m%d%H")
        o2 = o[(dtm >= start) & (dtm < end)]
        if result is None:
            result = o2
        else:
            result = pandas.concat([result, o2])
        ct = ct + datetime.timedelta(hours=1)
    return result


def load_observations_fortime(v_time, version="3"):
    result = None
    if v_time.hour % 6 == 0:
        result = load_observations_1file(v_time, version=version)
        result["weight"] = numpy.repeat(1, len(result.index))
        return result
    if v_time.hour % 6 <= 3:
        prev_time = v_time - datetime.timedelta(hours=v_time.hour % 6)
        prev_weight = 1.0
        result = load_observations_1file(prev_time, version=version)
        result["weight"] = numpy.repeat(prev_weight, len(result.index))
        return result
    prev_time = v_time - datetime.timedelta(hours=v_time.hour % 6)
    prev_weight = (3 - v_time.hour % 3) / 3.0
    result = load_observations_1file(prev_time, version=version)
    result["weight"] = numpy.repeat(prev_weight, len(result.index))
    next_time = prev_time + datetime.timedelta(hours=6)
    next_weight = 1 - prev_weight
    result2 = load_observations_1file(next_time, version=version)
    result2["weight"] = numpy.repeat(next_weight, len(result2.index))
    result = pandas.concat([result, result2])
    return result
