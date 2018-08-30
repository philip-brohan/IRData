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
This package retrieves and loads data from the `Twentieth Century Reanalysis (20CR) <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_.

It retrieves the data from the `20CR portal <http://portal.nersc.gov/project/20C_Reanalysis/>`_ at `NERSC <http://www.nersc.gov>`_.

At the moment, only version '2c' of 20CR is supported for public use. There is limited support for the pre-release of version 3 - versions '4.5.*' - see below.

Only hourly data is supported (no daily or monthly averages) for 5 surface variables:

* Mean-sea-level pressure: 'mslp'
* 2m air temperature: 'air.2m'
* Precipitation rate: 'prate'
* 10m meridional wind: 'uwnd.10m'
* 10m zonal wind: 'vwnd.10m'

Data retrieved is stored in directory $SCRATCH/20CR - the 'SCRATCH' environment variable must be set.

For example:

.. code-block:: python

    import datetime
    import IRData.twcr as twcr
    twcr.fetch('prate',
               datetime.datetime(1987,3,12),
               version='2c')

Will retrieve precipitation rate data for the selected date. 20CR2c data is fetched in one-calendar-year blocks, so this will retrieve data for the whole of 1987. The retrieval is slow, as the data has to be fetched from NERSC, but the retrieval is only run if necessary - if that year's data has been previously fetched and is already on local disc, the fetch command will detect this and return instantly.

Once the data has been fetched, 

.. code-block:: python

    pr=twcr.load('prate',
                 datetime.datetime(1987,3,12,15,15),
                 version='2c')

will then load the precipitation rates at quarter past 3pm on March 12 1987 from the retrieved dataset as an :obj:`iris.cube.Cube`. Note that as 20CR only provides data at 6-hourly or 3-hourly intervals, the value for 3:15pm will be interpolated between the outputs (to get uninterpolated data, only call load for times when 20CR has output). Also, as 20CR2c is an ensemble dataset, the result will include all 56 ensemble members.

Observations files are also available. They can be fetched with:

.. code-block:: python

    import datetime
    twcr.fetch_observations(datetime.datetime(1987,3,12,15,15),
                            version='2c')


Observations are also fetched in one-calendar-year blocks, so this will retrieve observations (from NERSC) for the whole of 1987. Again, the retrieval is only run if necessary - if that year's data has been previously fetched and is already on local disc, the fetch command will detect this and return instantly.

Once the observations have been fetched, load all the observations valid between two times with:

.. code-block:: python

    import datetime
    o=twcr.load_observations(datetime.datetime(1987,3,12,6),
                             datetime.datetime(1987,3,12,18),
                             version='2c')

It's also possible to load all the observations associated with a particular reanalysis field. 20CR assimilates observations every 6-hours, so there is one observations file for each 6-hourly assimilation run. Load all the observations available to the assimilation run for 12 noon on March 12 1987 (as a :obj:`pandas.DataFrame`) with:

.. code-block:: python

    o=twcr.load_observations_1file(datetime.datetime(1987,3,12,12),
                                   version='2c')

That's only possible for times that match an assimilation time (hour=0,6,12,18). For in-between times (interpolated fields), load all the observations contributing to the field with:

.. code-block:: python

    o=twcr.load_observations_fortime(datetime.datetime(1987,3,12,12),
                                     version='2c')

This gets all the observations from each field used in the interpolation, and assigns a weight to each one - the same as the weight used in interpolating the fields.

Pre-release version 3
---------------------

Version numbers beginning '4.5.' (mostly '4.5.1' and '4.5.2') are the pre-release data for 20CRv3 and all the functions described above will work in the same way, with the *major* caveat that the data are not yet released, so you can't just 'fetch' them. To get proto-v3 data, first `create the data files at NERSC <https://oldweather.github.io/20CRv3-diagnostics/extract_data/extract_data.html>`_ and then fetch them as with 2c, except you will be downloading the data by ssh. This means you will need to `setup your NERSC account to support passwordless ssh access from your local machine <http://www.nersc.gov/users/connecting-to-nersc/connecting-with-ssh/>`_ and add your NERSC account name to the fetch command:

.. code-block:: python

    import datetime
    import IRData.twcr as twcr
    twcr.fetch('prate',
               datetime.datetime(1987,3,12),
               version='4.5.1',
               user='pbrohan')

Note that proto-v3 data is fetched in 1-month blocks (rather than 1-year as for 2c).
All the 'load' functions then work exactly as for 2c.

Note: NERSC is soon to enforce multi-factor authentication which will mess this up. Some changes will be required.

|
"""

from utils import *
from load import *
from fetch import *
from observations import *
