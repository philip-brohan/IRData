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

# Fetch 20CR V3-preliminary data from NERSC and store it on $SCRATCH.

import os
import subprocess
import getpass
import datetime

from .utils import _get_data_file_name
from .utils import monolevel_analysis
from .utils import multilevel_analysis
from .utils import monolevel_forecast

def _get_remote_file_name(variable,year,month,
                          height=None,level=None,
                          version='4.5.1',user='pbrohan'):

    remote_dir=("%s@dtn02.nersc.gov:/global/cscratch1/sd/%s/"+
                "20CRv3.final/version_%s") % (user,user,version)
    
    if variable=='observations':
        remote_file="%s/%04d/%02d/observations/" % (remote_dir,
                     year,month)
        return(remote_file) 

    if (variable in monolevel_analysis or 
        variable in monolevel_forecast):
        remote_file="%s/%04d/%02d/%s.nc4" % (remote_dir,year,month,variable)
    elif variable in multilevel_analysis:
        if level is not None:
            remote_file="%s/%04d/%02d/%s.%dmb.nc4" % (remote_dir,year,month,variable,level)
        elif height is not None:
            remote_file="%s/%04d/%02d/%s.%dm.nc" % (remote_dir,year,month,variable,height)
        else:
            raise ValueError('No height or level specified for 3d variable')
    else:
        raise ValueError('Unsupported variable: %s' & variable)
    return remote_file


def fetch(variable,dtime,
          height=None,level=None,
          version='4.5.1',user='pbrohan'):
    """Get all data for one variable, for one month, from Cori SCRATCH directory at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        year  (:obj:`int`): Year to get data for.
        month (:obj:`int`): Month to get data for.
        height (:obj:`int`): Height above ground (m) for 3d variables. Variable must be in 20CR output at that exact height (no interpolation). Defaults to None - appropriate for 2d variables.
        level (:obj:`int`): Pressure level (hPa) for 3d variables. Variable must be in 20CR output at that exact pressure level (no interpolation). Defaults to None - appropriate for 2d variables.
        user  (:obj:`str`): NERSC userid to use in retrieval. Only needed for v3-preliminary data. Defaults to 'pbrohan'. This should be your NERSC username.

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """

    local_file=_get_data_file_name(variable,
                                   dtime.year,dtime.month,
                                   height,level,
                                   version=version)

    if ((variable != 'observations') and os.path.isfile(local_file)): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=_get_remote_file_name(variable,dtime.year,
                                      dtime.month,height,level,version,user)

    if(variable=='observations'):
        # Multiple files - use rsync
        local_file=os.path.dirname(local_file)
        cmd="rsync -Lr %s/ %s" % (remote_file,local_file)
        scp_retvalue=subprocess.call(cmd,shell=True) # Why need shell=True?
        if scp_retvalue!=0:
            raise Exception("Failed to retrieve observations. Code: %d" % scp_retvalue)
        
    else:
        # Single file - use scp
        cmd="scp %s %s" % (remote_file,local_file)
        scp_retvalue=subprocess.call(cmd,shell=True)
        if scp_retvalue!=0:
            raise Exception("Failed to retrieve data. Code: %d" % scp_retvalue)

