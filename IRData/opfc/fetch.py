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

# The functions in this module fetch MetO Operational data from MASS and
#   store it in $SCRATCH.
# Only works inside the Met Office.

import os
import subprocess
import datetime
import calendar
import iris

from .utils import _get_file_name
from .utils import _get_data_times
from .utils import _stash_from_variable_names
from .utils import monolevel_analysis

def fetch(variable,dtime,model='global',fctime=0):
    """Get data for for one month, from MASS. You can specify a variable, for consistency with related functions for other sources, but it gets all the supported variables because they are all in the same file on tape.

    As this function gets data from tape, it may take a long time (many minutes) to return.

    Data wil be stored locally in directory $SCRATCH/opfc, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        dtime (:obj:`datetime.datetime`): Date and time to get data for.
        model (:obj:`str`): Which forecast model to use (currently must be 'global').
        fctime (:obj:`int`): Forecast lead time (currently must be 0).

   Batches retrievals by the calendar month. If you specify a dtime very close to the start or end of a month, it will do the retrieval for the previous or next month as well (so it provides enough data to interpolate the field at exactly the time requested.

    Raises:
        StandardError: If variable is not a supported value, or if the requested data is not available on tape, or if the MASS system is down, or if the model requested is not supported.
 
    |
    """
    if model=='global':
        if dtime.hour%6 != 0:
            for dtm in _get_data_times(variable,dtime,fctime=fctime,model=model):
                fetch(variable,dtm,model=model,fctime=fctime)
        else:
            file_name=_get_file_name(variable,dtime,fctime=fctime,model=model)
            if os.path.isfile(file_name): return
            dname=os.path.dirname(file_name)
            startday="%04d%02d01" % (dtime.year,dtime.month)
            endday="%04d%02d%02d" % (dtime.year,dtime.month,
                calendar.monthrange(dtime.year,dtime.month)[1])
            stash=""
            for var in monolevel_analysis:
                stash += "%d:p0 " % _stash_from_variable_names(var,model=model).lbuser3()
            cmd=('. ~frtr/trui/stable/bin/trui_env.ksh\n . trui_python_env\n '+
                 'retr_from_opfc.py --model-name=global --cycle="00 06 12 18" '+
                 '--date="%s-%s" --forecast-time="0 1 2 3 4 5" '+
                 '--out-dir=%s ' +
                 '--stash="%s"\n') % (startday,endday,dname,stash)
            res = subprocess.run(cmd,shell=True)
            res.check_returncode() # Throw exception if not 0
    else:
        raise Exception("Unsupported model %s" % model)
    return

