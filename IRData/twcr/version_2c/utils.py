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

# Utility functions for version 2c

import os
import datetime

def _get_data_dir():
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_%s/" % (os.environ['SCRATCH'],'2c')
    return g

def _get_data_file_name(variable,year,type=None):
    """Return the name of the file containing data for the
       requested variable, at the specified time, from the
       20CR version."""
    base_dir=_get_data_dir()
    if type is None:
        name="%s/%04d/%s.nc" % (base_dir,year,variable)
    elif type=='normal':
        name="%s/normals/%s.nc" % (base_dir,variable)
    elif type=='standard.deviation':
        name="%s/standard.deviations/%s.nc" % (base_dir,variable)
    else:
        raise ValueError("Unsupported data type %s" % type)
    return name

def _adjust_dtime_for_type(year,month,day,hour,type):
    """Things like normals are stored with year set to 1981, so
        the date needs changing before doing the retrieval."""
    if type=='normal' or type=='standard.deviation':
        minute=int((hour%1)*60)
        hour=int(hour)
        # No normals for Feb 29th - use previous day
        if (month==2 and day==29):
            result=datetime.datetime(1981,month,28,hour,minute)
        else:
            result=datetime.datetime(1981,month,day,hour,minute)
    else:
        raise ValueError('Unsupported type %s' % type)
    return (result.year,result.month,result.day,result.hour)
 
