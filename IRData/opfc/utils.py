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

# Utility functions for file and variable name mapping 
#   for MetO operational data.

import os
import datetime
import calendar
import iris

# Names of analysis variables supported
monolevel_analysis=('prmsl','air.2m','uwnd.10m','vwnd.10m',
                    'icec','tsurf','orog','lsmask','prate')

# Variable name to iris stash code
#  See https://code.metoffice.gov.uk/trac/nwpscience/wiki/ModelInfo
def _stash_from_variable_names(variable,model='global'):

    if model=='global':
        if(variable=='prmsl'):
            return iris.fileformats.pp.STASH(1,16,222)
        if(variable=='tsurf'):
            return  iris.fileformats.pp.STASH(1,0,24)
        if(variable=='air.2m'):
            return  iris.fileformats.pp.STASH(1,3,236)
        if(variable=='lsmask'):
            return  iris.fileformats.pp.STASH(1,0,30)
        if(variable=='orog'):
            return  iris.fileformats.pp.STASH(1,0,33)
        if(variable=='icec'):
            return  iris.fileformats.pp.STASH(1,0,31)
        if(variable=='uwnd.10m'):
            return  iris.fileformats.pp.STASH(1,3,225)
        if(variable=='vwnd.10m'):
            return  iris.fileformats.pp.STASH(1,3,226)
        if(variable=='sst'):
            return _translate_for_variable_names('tsurf',model=model)
        if(variable=='prate'):
            return  iris.fileformats.pp.STASH(1,5,216)
        raise Exception("Unsupported variable %s" % variable)
    raise Exception("Unsupported model %s" % model)

# Directory to keep downloaded data in
def _get_data_dir():
    scratch=os.getenv('SCRATCH')
    if scratch is None:
        raise Exception("SCRATCH environment variable is undefined")
    if not os.path.isdir(scratch):
        raise Exception("Scratch directory %s does not exist" % 
                               scratch)
    base_file = "%s/opfc" % scratch
    return base_file

# File name for data for a given variable and time
def _get_file_name(variable,dtime,
                   fctime=0,
                   model='global'):
    base_dir=_get_data_dir()
    startday="%04d%02d01" % (dtime.year,dtime.month)
    endday="%04d%02d%02d" % (dtime.year,dtime.month,
        calendar.monthrange(dtime.year,dtime.month)[1])

    if model=='global':    
        dir_name="%s/mo_glm_%s-%s" % (base_dir,startday,
                                               endday)
        if variable=='orog':
            file_name="%s/prodm_op_gl-mn_%04d%02d%02d_%02d_%03d.pp" % (
                          dir_name,dtime.year,dtime.month,dtime.day,
                          dtime.hour,fctime)
        else:
            file_name="%s/prods_op_gl-mn_%04d%02d%02d_%02d_%03d.pp" % (
                          dir_name,dtime.year,dtime.month,dtime.day,
                          dtime.hour,fctime)
    else:
        raise Exception("Unsupported model %s" % model)

    return file_name

# Get the before and after times with data for a time point that will
#  need interpolation.
def _get_data_times(variable,dtime,
                    fctime=0,
                    model='global'):
    if dtime.hour%6 == 0:
        return([dtime])
    else:
       return([dtime-datetime.timedelta(hours=dtime.hour%6),
               dtime+datetime.timedelta(hours=6-dtime.hour%6)])


    
