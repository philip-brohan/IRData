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
"""
This package retrieves and loads data from the `CERA-20C reanalysis <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/cera-20c>`_.

To retrieve the data, it uses the `ECMWF Public data API <https://software.ecmwf.int/wiki/display/WEBAPI/ECMWF+Web+API+Home>`_. You will need to install a key as described in `the API documentation <https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets>`_. Note that this is the same system used by `IRData.era5` - the same key will let you use that as well.

Only hourly data is supported (no daily or monthly averages) for 7 surface variables:

* Mean-sea-level pressure: 'mslp'
* 2m air temperature: 'air.2m'
* Precipitation rate: 'prate'
* 10m meridional wind: 'uwnd.10m'
* 10m zonal wind: 'vwnd.10m'
* Sea-surface temperature: 'sst'
* Sea-ice coverage: 'icec'

Data retrieved is stored in directory $SCRATCH/CERA_20C - the 'SCRATCH' environment variable must be set.

For example:

.. code-block:: python

    import datetime
    import IRData.cera20c as cera20c
    cera20c.fetch('prate',datetime.datetime(1969,3,12))

will retrieve precipitation rate data for the selected date. CERA20C data is fetched in one-calendar-month blocks, so this will retrieve data for the whole of March 1969. The retrieval is slow, as the data has to be fetched from MARS at ECMWF, but the retrieval is only run if necessary - if that month's data has been previously fetched and is already on local disc, the fetch command will detect this and return instantly.

Once the data has been fetched, 

.. code-block:: python

    pr=cera20c.load('prate',datetime.datetime(1969,3,12,15,15))

will then load the precipitation rates at quarter past 3pm on March 12 1969 from the retrieved dataset as a :class:`iris.cube.Cube`. Note that as CERA only provides data at 3-hourly intervals, the value for 3:15pm will be interpolated between the 15:00 and 18:00 outputs (to get uninterpolated data, only call load for times when CERA-20C has output). Also, as CERA is an ensemble dataset, the result will include all 10 ensemble members.

Note that precipitation in CERA-20C is reported as metres accumulated, and it accumulates over the whole 27-hour forecast, so it reports precip at 15:00 as (accumulated precip at 12:00)+(accumulation in the period 12-15). This module removes the across-timestep accumulation, so 'loading' precip at 15:00 only gives the accumulation in the period 12-15, and the units are 'm accumulated in the last 3-hours'. It is this 3-hour-accumulation that is interpolated if you 'load' the precipitation for a period between timesteps.

|
"""

from utils import *
from fetch import *
from load import *

