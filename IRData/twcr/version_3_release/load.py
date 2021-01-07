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

# Load V3-final data from a local file

import os
import os.path
import iris
import iris.time
import datetime
import warnings

from .utils import _get_data_file_name
from .utils import monolevel_analysis

# Need to add coordinate system metadata so they work with cartopy
coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)


def _is_in_file(variable, hour):
    """Is the variable available for this time?
    Or will it have to be interpolated?"""
    if hour % 3 == 0:
        return True
    return False


def _get_previous_field_time(variable, year, month, day, hour):
    """Get the latest time, before the given time,
    for which there is saved data"""
    return {"year": year, "month": month, "day": day, "hour": int(hour / 3) * 3}


def _get_next_field_time(variable, year, month, day, hour):
    """Get the earliest time, after the given time,
    for which there is saved data"""
    dr = {"year": year, "month": month, "day": day, "hour": int(hour / 3) * 3 + 3}
    if dr["hour"] >= 24:
        d_next = datetime.date(dr["year"], dr["month"], dr["day"]) + datetime.timedelta(
            days=1
        )
        dr = {
            "year": d_next.year,
            "month": d_next.month,
            "day": d_next.day,
            "hour": dr["hour"] - 24,
        }
    return dr


def _get_slice_at_hour_at_timestep(
    variable, year, month, day, hour, version="3", member=None
):
    """Get the cube with the data, given that the specified time
    matches a data timestep."""
    if not _is_in_file(variable, hour):
        raise ValueError("Invalid hour - data not in file")
    if member is None:
        res = iris.cube.CubeList()
        for mem in range(1, 81):
            res.append(
                _get_slice_at_hour_at_timestep(
                    variable, year, month, day, hour, version=version, member=mem
                )
            )
            if mem > 1:
                res[mem - 1].attributes = res[0].attributes
            res[mem - 1].add_aux_coord(iris.coords.AuxCoord(mem, long_name="member"))
        return res.merge_cube()
    file_name = _get_data_file_name(
        variable, year, month, version=version, member=member
    )
    time_constraint = iris.Constraint(
        time=iris.time.PartialDateTime(year=year, month=month, day=day, hour=hour)
    )
    try:
        with warnings.catch_warnings():  # Iris is v.fussy
            warnings.simplefilter("ignore")
            hslice = iris.load_cube(file_name, time_constraint)
    except iris.exceptions.ConstraintMismatchError:
        raise Exception(
            "%s not available for %04d-%02d-%02d:%02d"
            % (variable, year, month, day, hour)
        )

    # Enhance the names and metadata for iris/cartopy
    hslice.coord("latitude").coord_system = coord_s
    hslice.coord("longitude").coord_system = coord_s
    # Get rid of unnecessary height dimensions
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hslice = hslice.collapsed("height", iris.analysis.MEAN)
    except Exception:
        pass
    return hslice


def load(variable, dtime, version="3", member=None):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/20CR.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        dtime (:obj:`datetime.datetime`): Date and time to load data for.
        version (:obj:`str`): Reanalysis version (e.g. '4.5.1') defaults to '3'
        member (:obj:`int`): Which member to load. Defaults to None - load all 80 members.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that 20CR data is only output every 3 hours, so if hour%3!=0, the result may be linearly interpolated in time.

    Raises:
        StandardError: Data not on disc.

    |
    """
    dhour = dtime.hour + dtime.minute / 60.0 + dtime.second / 3600.0
    if _is_in_file(variable, dhour):
        return _get_slice_at_hour_at_timestep(
            variable,
            dtime.year,
            dtime.month,
            dtime.day,
            dhour,
            version=version,
            member=member,
        )
    previous_step = _get_previous_field_time(
        variable, dtime.year, dtime.month, dtime.day, dhour
    )
    next_step = _get_next_field_time(
        variable, dtime.year, dtime.month, dtime.day, dhour
    )
    dt_current = dtime
    dt_previous = datetime.datetime(
        previous_step["year"],
        previous_step["month"],
        previous_step["day"],
        previous_step["hour"],
    )
    dt_next = datetime.datetime(
        next_step["year"], next_step["month"], next_step["day"], next_step["hour"]
    )
    s_previous = _get_slice_at_hour_at_timestep(
        variable,
        previous_step["year"],
        previous_step["month"],
        previous_step["day"],
        previous_step["hour"],
        version=version,
        member=member,
    )
    s_next = _get_slice_at_hour_at_timestep(
        variable,
        next_step["year"],
        next_step["month"],
        next_step["day"],
        next_step["hour"],
        version=version,
        member=member,
    )
    # Iris won't merge cubes with different attributes
    s_previous.attributes = s_next.attributes
    s_next = iris.cube.CubeList((s_previous, s_next)).merge_cube()
    s_next = s_next.interpolate([("time", dt_current)], iris.analysis.Linear())
    return s_next
