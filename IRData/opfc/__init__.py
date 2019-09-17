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
This package retrieves and loads data from the Met Office Operational Forecast Archive.

It will only work inside the Met Office (needs access to the MASS archive).

Only hourly data is supported (no daily or monthly averages) for 7 surface variables:

* Mean-sea-level pressure: 'mslp'
* 2m air temperature: 'air.2m'
* Precipitation rate: 'prate'
* 10m meridional wind: 'uwnd.10m'
* 10m zonal wind: 'vwnd.10m'
* Surface temperature: 'tsurf' - use 'sst' to get just the ocean component
* Sea-ice coverage: 'icec'
* Land Mask: 'lsmask'
* Orography: 'orog'

Data retrieved is stored in directory $SCRATCH/opfc - at the moment only the 'global deterministic' model is supported.

For example:

.. code-block:: python

    import datetime
    import IRData.opfc as opfc
    opfc.fetch('prate',
               datetime.datetime(2015,3,12),
               model='global')

will retrieve precipitation rate data for the selected date. Data is fetched in one-calendar-month blocks, so this will retrieve data for the whole of March 2015. The retrieval can slow, as the data has to be fetched from tape, but the retrieval is only run if necessary - if that month's data has been previously fetched and is already on local disc, the fetch command will detect this and return instantly.

Once the data has been fetched, 

.. code-block:: python

    pr=opfc.load('prate',
                 datetime.datetime(2015,3,12,15,15),
                 model='global')

will then load the precipitation rates at quarter past 3pm on March 12 2015 from the retrieved dataset as a :class:`iris.cube.Cube`. Note that as the analysis is only run at 6-hourly intervals, the value for 3:15pm will be interpolated between the outputs. 

|
"""

from .utils import *
from .fetch import *
from .load import *

