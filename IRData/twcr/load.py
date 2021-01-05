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

# Load 20CR data from local files.

from . import version_2c
from . import version_3
from . import version_3_release
import datetime

def load(variable,dtime,
         height=None,level=None,ilevel=None,
         version=None,type=None,member=None):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        dtime (:obj:`datetime.datetime`): Date and time to load data for.
        height (:obj:`int`): Height above ground (m) for 3d variables. Only used in v3. Variable must be in 20CR output at that exact height (no interpolation). Defaults to None - appropriate for 2d variables.
        level (:obj:`int`): Pressure level (hPa) for 3d variables. Only used in v3. Variable must be in 20CR output at that exact pressure level (no interpolation). Defaults to None - appropriate for 2d variables.
        ilevel (:obj:`int`): Isentropic level (K) for 3d variables. Only used in v3. Variable must be in 20CR output at that exact pressure level (no interpolation). Defaults to None - appropriate for 2d variables.
        member (:obj:`int`): Member to load (version 3 only). Defaults to None - load all 80 members.
        version (:obj:`str`): 20CR version to load data from.
        type (:obj:`str`): If None load raw data (default). If 'normal, or standard.deviations load those derived data.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that 20CR data is only output every 6 hours (v2c prmsl) or 3 hours, so if hour%3!=0, the result may be linearly interpolated in time.

    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch`

    |
    """
    if version=='2c':
        return version_2c.load(variable,dtime,type=type)
    if version=='3' or version[0]=='4' or version[0]=='0':
        return version_3_release.load(variable,dtime,version=version,member=member)
    raise Exception('Invalid version number %s' % version)

