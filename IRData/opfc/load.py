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

# The functions in this module provide the main way to load
# MetO Operational data.

import os
import os.path
import iris
import iris.time
import datetime
import numpy as np

from .utils import _get_file_name
from .utils import _get_data_times
from .utils import _stash_from_variable_names
from .utils import monolevel_analysis

# Need to add coordinate system metadata so they work with cartopy
coord_s=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

def _is_in_file(variable,year,month,day,hour,model='global'):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if model=='global' and hour%6==0:
        return True
    return False

def _get_previous_field_time(variable,year,month,day,hour,model='global'):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    if model=='global':
        return {'year':year,'month':month,'day':day,'hour':int(hour/6)*6}
        raise Exception("Unknown model %s" % model)

def _get_next_field_time(variable,year,month,day,hour,model='global'):
    """Get the earliest time, after the given time,
                     for which there is saved data"""  
    if model=='global':
       dr = {'year':year,'month':month,'day':day,'hour':int(hour/6)*6+6}
    else:
       raise Exception("Unknown model %s" % model) 
    if dr['hour']>=24:
        d_next= ( datetime.date(dr['year'],dr['month'],dr['day']) 
                 + datetime.timedelta(days=1) )
        dr = {'year':d_next.year,'month':d_next.month,'day':d_next.day,
              'hour':dr['hour']-24}
    return dr

def _get_slice_at_hour_at_timestep(variable,year,month,day,hour,
                                   model='global',fctime=0):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not _is_in_file(variable,year,month,day,hour,model=model):
        raise ValueError("Invalid hour - data not in file")
    file_name=_get_file_name(variable,datetime.datetime(year,month,day,int(hour)),
                                   model=model,fctime=fctime)
    if not os.path.isfile(file_name):
        raise Exception(("%s for %04d/%02d not available"+
                             " might need oper.fetch") % (variable,
                                                             year,month))
    stsh=_stash_from_variable_names(variable,model=model)
    hslice=iris.load_cube(file_name,
                          iris.AttributeConstraint(STASH=stsh))

    return hslice

def load(variable,dtime,
         model='global',fctime=0):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/opfc, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        dtime (:obj:`datetime.datetime`): Run date and time to load data for.
        model (:obj:`str`): Model to get data from - currently must be 'global'.
        fctime (:obj:`int`): Forecast time (hours) - currently must be 0.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that opfc data is only output every 6 hours (global model), so if hour%6!=0, the result may be linearly interpolated in time.

    Raises:
        Exception: Data not on disc - see :func:`fetch`

    |
    """
    if variable not in monolevel_analysis:
        raise Exception("Unsupported variable %s" % variable)
    dhour=dtime.hour+dtime.minute/60.0+dtime.second/3600.0
    if _is_in_file(variable,
                   dtime.year,dtime.month,dtime.day,dhour,
                   model=model):
        return(_get_slice_at_hour_at_timestep(variable,dtime.year,
                                              dtime.month,dtime.day,
                                              dhour,model=model,
                                              fctime=fctime))
    previous_step=_get_previous_field_time(variable,dtime.year,dtime.month,
                                           dtime.day,dhour,model=model)
    next_step=_get_next_field_time(variable,dtime.year,dtime.month,
                                   dtime.day,dhour,model=model)
    dt_current=dtime
    dt_previous=datetime.datetime(previous_step['year'],
                                  previous_step['month'],
                                  previous_step['day'],
                                  previous_step['hour'])
    dt_next=datetime.datetime(next_step['year'],
                              next_step['month'],
                              next_step['day'],
                              next_step['hour'])
    s_previous=_get_slice_at_hour_at_timestep(variable,
                                              previous_step['year'],
                                              previous_step['month'],
                                              previous_step['day'],
                                              previous_step['hour'],
                                              model=model,
                                              fctime=fctime)
    s_next=_get_slice_at_hour_at_timestep(variable,
                                          next_step['year'],
                                          next_step['month'],
                                          next_step['day'],
                                          next_step['hour'],
                                          model=model,
                                          fctime=fctime)
 
    # Iris won't merge cubes with different attributes
    s_previous.attributes=s_next.attributes
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',dt_current)],iris.analysis.Linear())
    return s_next

