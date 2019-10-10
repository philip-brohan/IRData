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
from .utils import _stash_from_variable_names
from .utils import monolevel_analysis

def _get_file_times(variable,validity_time,model='global',methods=None):
    """Get the times for which data are available, needed to interpolate
          the data at the given validity time.
      Will be one time (=validity time) if the data for the requested time
       are on disc., and two times (closest previous time on disc and closest
       subsequent time on disc) otherwise."""
    if model=='global':
        if variable=='prate_a':
            if validity_time.minute==30:
                return([validity_time])
            else:
                if validity_time.minute<30:
                    prevt=(validity_time-datetime.timedelta(hours=1)
                                +datetime.timedelta(minutes=30-validity_time.minute))
                else:
                    prevt=(validity_time-datetime.timedelta(minutes=validity_time.minute-30))
                return([prevt,
                        prevt+datetime.timedelta(hours=1)])
        else:
            if validity_time.minute==0:
                return([validity_time])
            else:
                prevt=(validity_time-datetime.timedelta(minutes=validity_time.minute))
                return([prevt,
                        prevt+datetime.timedelta(hours=1)])            
    else:
        raise Exception("Unknown model %s" % model)

def _get_fcst_reference_time(variable,validity_time,model='global',methods=None):
    """Get the most recent forecast reference time for a variable at validity_time.
         validity_time must be a time for which forecast data is available (the output
            of _get_file_times)."""
    if model=='global':
        if variable=='prate_a':
            if validity_time.hour >= 23:
                return validity_time+datetime.timedelta(minutes=30)
            else:
                fcrt=validity_time-datetime.timedelta(minutes=validity_time.minute)
                fcrt -= datetime.timedelta(hours=fcrt.hour%6)
                return fcrt
        else:
            return validity_time - datetime.timedelta(hours=validity_time.hour%6)
    else:
        raise Exception("Unknown model %s" % model)
            
def _get_fcst_period(variable,validity_time,model='global',methods=None):
    """Get the period between the forecast reference time and the validity time.
         validity_time must be a time for which forecast data is available (the output
            of _get_file_times)."""

    fp = validity_time-_get_fcst_reference_time(variable,validity_time,
                                                  model=model,methods=methods)
    if model=='global':
        if variable=='prate_a': # Want bounds, not period centre
            fp=[fp-datetime.timedelta(minutes=30),
                fp+datetime.timedelta(minutes=30)]
    else:
        raise Exception("Unknown model %s" % model)

    return fp

def _get_slice_at_hour_at_timestep(variable,validity_time,
                                   methods=None,
                                   model='global'):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    file_name=_get_file_name(variable,validity_time,model=model,methods=methods)
    if not os.path.isfile(file_name):
        raise Exception(("Data for %04d/%02d/%02d not available"+
                             " might need oper.fetch") % validity_time.strftime("%Y-%m-%d"))
    if variable=='prate_a':
        tp=_get_fcst_period(variable,validity_time,model=model,methods=methods)
        tp[0]=tp[0].days*24+tp[0].seconds//3600
        tp[1]=tp[1].days*24+tp[1].seconds//3600
        ftco =iris.Constraint(forecast_period = lambda t: t.bound is not None and t.bound[0]==tp[0] and t.bound[1]==tp[1])
    else:
        ftco =iris.Constraint(forecast_period=_get_fcst_period(variable,validity_time,
                                             model=model,methods=methods).seconds//3600)
    ftfr=iris.Constraint(forecast_reference_time=_get_fcst_reference_time(variable,
                                           validity_time,model=model,methods=methods))
    stco=iris.AttributeConstraint(STASH=_stash_from_variable_names(variable,
                                                               model=model))
    hslice=iris.load_cube(file_name, stco & ftco & ftfr)
    return hslice

def load(variable,validity_time,methods=None,model='global'):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/opfc, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        validity_time (:obj:`datetime.datetime`): Date and time to load data for.
        model (:obj:`str`): Model to get data from - currently must be 'global'.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that opfc data is only output every hour (global model), so the result may be linearly interpolated in time.

    Raises:
        Exception: Data not on disc - see :func:`fetch`

    |
    """
    if variable not in monolevel_analysis:
        raise Exception("Unsupported variable %s" % variable)
    ftimes=_get_file_times(variable,validity_time,model=model,methods=methods)
    if len(ftimes)==1:
        return _get_slice_at_hour_at_timestep(variable,ftimes[0],methods=methods,model=model)
    s_previous=_get_slice_at_hour_at_timestep(variable,ftimes[0],methods=methods,model=model)
    s_next=_get_slice_at_hour_at_timestep(variable,ftimes[1],methods=methods,model=model)
 
    # Iris won't merge cubes with different attributes
    s_previous.attributes=s_next.attributes
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',validity_time)],iris.analysis.Linear())
    return s_next

