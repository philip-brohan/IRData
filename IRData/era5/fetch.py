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

#The functions in this module fetch ERA5 data from ECMWF and
# store it in $SCRATCH.

import os
import subprocess
import datetime
import calendar
import ecmwfapi

from .utils import _hourly_get_file_name
from .utils import _translate_for_file_names
from .utils import monolevel_analysis
from .utils import monolevel_forecast

def fetch(variable,dtime,stream='enda'):
    """Get all data for one variable, for one month, from ECMWF's archive.

    Data wil be stored locally in directory $SCRATCH/ERA5, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        dtime (:obj:`datetime.datetime`): Date and time to get data for.
        month (:obj:`int`): Month to get data for (1-12).
        stream (:obj:`str`): Analysis stream to use, can be 'enda' - ensemble DA, or 'oper' - high res single member.

    Will retrieve the data for the year and month of the given date-time. If the selected time is very close to the end of the calendar month, loading data for that time will also need data from the next calendar month (for interpolation). In this case, also fetch the data for the next calendar month. 

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """
    ndtime=dtime+datetime.timedelta(hours=3)
    if stream=='oper': 
        ndtime=dtime+datetime.timedelta(hours=1)
    if ndtime.month!=dtime.month:
        fetch(variable,ndtime)
    if variable in monolevel_analysis:
        return _fetch_analysis_data_for_month(variable,dtime.year,
                                              dtime.month,
                                              stream=stream)
    if variable in monolevel_forecast:
        return _fetch_forecast_data_for_month(variable,dtime.year,
                                              dtime.month,
                                              stream=stream)
    raise Exception("Unsupported variable %s" % variable)

def _fetch_analysis_data_for_month(variable,year,month,
                                   stream='enda'):
        
    local_file=_hourly_get_file_name(variable,year,month,
                                     stream=stream)
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    if stream=='oper':
        grid='0.25/0.25'
        server = ecmwfapi.ECMWFDataServer()
        server.retrieve({
            'dataset'   : 'era5',
            'stream'    : 'oper',
            'type'      : 'an',
            'levtype'   : 'sfc',
            'param'     : _translate_for_file_names(variable),
            'grid'      : '0.25/0.25',
            'time'      : '0/to/23/by/1',
            'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                           (year,month,1,
                            year,month,
                            calendar.monthrange(year,month)[1]),
            'format'    : 'netcdf',
            'target'    : local_file
        })
    elif stream=='enda':
        server = ecmwfapi.ECMWFDataServer()
        server.retrieve({
            "class"   : "ea",
            "dataset" : "era5",
            'date'    : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                           (year,month,1,
                            year,month,
                            calendar.monthrange(year,month)[1]),
            "expver"  : "1",
            "levtype" : "sfc",
            "number"  : "0/1/2/3/4/5/6/7/8/9",
            "param"   : _translate_for_file_names(variable),
            "stream"  : "enda",
            "time"    : "0/to/21/by/3",
            "type"    : "an",
            'grid'    : '0.5/0.5',
            'format'  : 'netcdf',
            "target"  : local_file
        })
    else:
        raise Exception("Unsupported stream %s" % stream)
    

def _fetch_forecast_data_for_month(variable,year,month,
                                   stream='enda'):
        
    # Need two sets of forecast data - from the runs at 6 and 18
    for start_hour in (6,18):

        local_file=_hourly_get_file_name(variable,year,month,
                                    fc_init=start_hour,stream=stream)
        if os.path.isfile(local_file):
            # Got this data already
            continue

        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        if stream=='oper':
            server = ecmwfapi.ECMWFDataServer()
            server.retrieve({
                'dataset' : 'era5',
                'stream'  : 'oper',
                'type'    : 'fc',
                'levtype' : 'sfc',
                'param'   : _translate_for_file_names(variable),
                'grid'    : '0.25/0.25',
                'time'    : "%02d" % start_hour,
                'step'    : '0/to/18/by/1',
                'date'    : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                               (year,month,1,
                                year,month,
                                calendar.monthrange(year,month)[1]),
                'format'  : 'netcdf',
                'target'  : local_file
            })
        elif stream=='enda':
            server = ecmwfapi.ECMWFDataServer()
            server.retrieve({
                "class"   : "ea",
                "dataset" : "era5",
                'date'    : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                               (year,month,1,
                                year,month,
                                calendar.monthrange(year,month)[1]),
                "expver"  : "1",
                "levtype" : "sfc",
                "number"  : "0/1/2/3/4/5/6/7/8/9",
                "param"   : _translate_for_file_names(variable),
                "stream"  : "enda",
                'time'    : "%02d" % start_hour,
                'step'    : '0/to/18/by/3',
                "type"    : "fc",
                'grid'    : '0.5/0.5',
                'format'  : 'netcdf',
                "target"  : local_file
            })
        else:
            raise Exception("Unsupported stream %s" % stream)


