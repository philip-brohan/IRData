IRData: Accessing synoptic-timescale Reanalyis Data with Iris
=============================================================

This code library extends `Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_ in providing tools for accessing reanalysis data. It uses Iris data structures and methods for handling the data, and extends it by providing functions for using synoptic-timescale reanalysis data from several sources.

The idea is have an API for loading synoptic-timescale reanalysis data into an :class:`iris.cube.Cube`. That is, for a requirement like:

    "From the Twentieth Century Reanalysis version 2c, load the 2m air temperature at 7am (UTC) on 16th October 1987."

to have code that would find and download the data, and then provide it as a cube, interpolating to the requested time as necessary. 

This module provides such an API, for several reanalyses. The request above is:

.. code-block:: python

    import datetime
    dtime=datetime.datetime(1987,10,16,7)
    import IRData.twcr as twcr
    twcr.fetch('air.2m',dtime,version='2c')
    mycube=twcr.load('air.2m',dtime,version='2c')

Data is loaded in two steps:

1) First a block of data is 'fetched' from the reanalysis master archive and stored on local disk (in directory $SCRATCH). This step is slow (archives are typically on tape and may be on the other side of the world). Data is fetched in 1-calendar-month blocks (1 year blocks for 20CR2c).
2) Then the data for a single point in time  is 'loaded' from the local disc copy. This step is fast.

There is one sub-package for each of several data sources; each with `fetch` methods for getting a copy of the data from a remote server to a local filesystem, and `load` methods for loading iris cubes from the fetched data. 

Installation instructions:

.. toctree::
   :maxdepth: 1

   install
 
Data sources:

.. toctree::
   :maxdepth: 2
 
   subdata/data_20CR
   subdata/data_cera20c
   subdata/data_era5

|

Note that this is one person's personal library: I have no resources for support or extension beyond what is necessary for my own research. You are welcome to re-use any part of it (subject to the license, see below), but you would almost certainly be better advised to copy any bits you like and incoporate them into your own codebase than to rely on the stability of this.

The code in this library is licensed under the terms of the `GNU Lesser General Public License <https://www.gnu.org/licenses/lgpl.html>`_. The documentation under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_.

