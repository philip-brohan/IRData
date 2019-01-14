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
import datetime

def load(variable,dtime,version=None):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        dtime (:obj:`datetime.datetime`): Date and time to load data for.
        version (:obj:`str`): 20CR version to load data from.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that 20CR data is only output every 6 hours (prmsl) or 3 hours, so if hour%3!=0, the result may be linearly interpolated in time.

    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch`

    |
    """
    if version=='2c':
        return version_2c.load(variable,dtime)
    if version[0:2] == '4.':
        return version_3.load(variable,dtime,version=version)
    raise Exception('Invalid version number %s' % version)

