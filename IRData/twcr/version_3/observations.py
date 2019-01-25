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

# Handle observations for version 3-preliminary

import datetime
import os
import os.path
import subprocess
import pandas
import numpy
import getpass

from .utils import _get_data_dir

def _observations_remote_file(year,month,version,user='pbrohan'):
    return (("%s@dtn02.nersc.gov:/global/cscratch1/sd/%s/"+
            "20CRv3.final/version_%s/%04d/%02d/observations/") %
             (user,user,version,year,month))

def _observations_file_name(year,month,day,hour,version):
    return ("%s/observations/%04d/%04d%02d%02d%02d_psobs_posterior.txt" % 
                            (_get_data_dir(version),year,year,month,day,hour))

def fetch_observations(dtime,version='4.5.1',user='pbrohan'):

    ndtime=dtime+datetime.timedelta(hours=6)
    if ndtime.year!=dtime.year:
        fetch_observations(ndtime)
    o_dir= "%s/observations/%04d" % (_get_data_dir(version),dtime.year)
    if os.path.exists(o_dir):
        if len(os.listdir(o_dir)) >= 1460:
            return
    else:
        os.makedirs(o_dir)

    # Multiple files, use rsync
    r_dir=_observations_remote_file(dtime.year,dtime.month,version,user)
    cmd="rsync -Lr %s/ %s" % (r_dir,o_dir)
    scp_retvalue=subprocess.call(cmd,shell=True) # Why need shell=True?
    if scp_retvalue!=0:
        raise Exception("Failed to retrieve observations. Code: %d" % scp_retvalue)

def load_observations_1file(dtime,version):
    """Retrieve all the observations for an individual assimilation run."""
    of_name=_observations_file_name(dtime.year,dtime.month,
                                    dtime.day,dtime.hour,version)
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o=pandas.read_fwf(of_name,
                       colspecs=[(0,19),
                                 (20,50),
                                 (52,64),
                                 (66,68),
                                 (69,72),
                                 (74,80),
                                 (81,87),
                                 (88,95),
                                 (97,102),
                                 (103,110),
                                 (111,112),
                                 (113,123),
                                 (124,134),
                                 (135,145),
                                 (146,156),
                                 (157,167),
                                 (168,175),
                                 (176,183),
                                 (184,191),
                                 (192,200),
                                 (201,205),
                                 (206,213),
                                 (214,221),
                                 (222,223)],
                       header=None,
                       encoding="ISO-8859-1",
                       names=['UID',
                              'Name',
                              'ID',
                              'Type',
                              'NCEP.Type',
                              'Longitude',
                              'Latitude',
                              'Observed',
                              'Time.offset',
                              'Observed.2',
                              'Skipped',
                              'Bias.correction',
                              'Obfit.prior',
                              'Obfit.post',
                              'Obsprd.prior',
                              'Obsprd.post',
                              'Oberrvar.orig.out',
                              'Oberrvar.out',
                              'Oberrvar.use',
                              'Paoverpb.save',
                              'Prob.gross.error',
                              'Localization.length.scale',
                              'Lnsigl',
                              'QC.failure.flag'],
                       converters={'UID':  str,
                                   'Name': str,
                                   'ID':   str,
                                   'Type': str,
                                   'NCEP.Type': int, 
                                   'Longitude': float, 
                                   'Latitude': float, 
                                   'Observed': float,
                                   'Time.offset': float,
                                   'Observed.2': float,
                                   'Skipped': int,
                                   'Bias.correction': float,
                                   'Obfit.prior': float,
                                   'Obfit.post': float,
                                   'Obsprd.prior': float,
                                   'Obsprd.post': float,
                                   'Oberrvar.orig.out': float,
                                   'Oberrvar.out': float,
                                   'Oberrvar.use': float,
                                   'Paoverpb.save': float,
                                   'Prob.gross.error': float,
                                   'Localization.length.scale': float,
                                   'Lnsigl': float,
                                   'QC.failure.flag': int},
                       na_values=['NA','*','***','*****','*******','**********',
                                          '-99','9999','-999','9999.99','10000.0',
                                          '-9.99',
                                          '999999999999','9'],
                       comment=None)
    return(o)



def load_observations(start,end,version):
    result=None
    ct=start
    while(ct<end):
        if(int(ct.hour)%6!=0):
           ct=ct+datetime.timedelta(hours=1)
           continue 
        o=load_observations_1file(ct.year,ct.month,ct.day,ct.hour,version)
        dtm=pandas.to_datetime(o.UID.str.slice(0,10),format="%Y%m%d%H")
        o2=o[(dtm>=start) & (dtm<end)]
        if(result is None):
            result=o2
        else:
            result=pandas.concat([result,o2])
        ct=ct+datetime.timedelta(hours=1)
    return(result)

def load_observations_fortime(v_time,version):
    result=None
    if v_time.hour%6==0:
        result=load_observations_1file(v_time,version)
        result['weight']=numpy.repeat(1,len(result.index))
        return result
    if v_time.hour%6<=3:
        prev_time=v_time-datetime.timedelta(hours=v_time.hour%6)
        prev_weight=1.0
        result=load_observations_1file(prev_time,version)
        result['weight']=numpy.repeat(prev_weight,len(result.index))
        return result
    prev_time=v_time-datetime.timedelta(hours=v_time.hour%6)
    prev_weight=(3-v_time.hour%3)/3.0
    result=load_observations_1file(prev_time,version)
    result['weight']=numpy.repeat(prev_weight,len(result.index))
    next_time=prev_time+datetime.timedelta(hours=6)
    next_weight=1-prev_weight
    result2=load_observations_1file(next_time,version)
    result2['weight']=numpy.repeat(next_weight,len(result2.index))
    result=pandas.concat([result,result2])
    return result
