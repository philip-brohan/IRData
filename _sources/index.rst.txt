OWData: An API for accessing synoptic-timescale reanalyis data
==============================================================

This code library extends `Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_ in providing tools for accessing general circulation model (GCM) data. It uses Iris data structures and methods for handling the data, and adds to it by providing functions for importing synoptic-timescale reanalysis data from several sources.

The idea is have an API for loading synoptic-timescale reanalysis data into an :class:`iris.cube.Cube`. That is, to say something like:

'from the CERA20C reanalysis, load the 2m air temperature at 7am (utc) on 16th October 1987.`

and the code would find and download the data, interpolating to the requested time as necessary. This module provides such an API, for several reanalyses. The request above is:

.. code-block:: python

    import datetime
    dtime=datetime.datetime(1987,10,16,7)
    import OWData.cera20c as cera20c
    cera20c.fetch('air.2m',dtime)        # Slow, but only needed the first time
    mycube=cera20c.load('air.2m',dtime)

There is one sub-package for each of several data sources, with `fetch` methods for getting a copy of the data from a remote server to a local filesystem. and `load` methods for loading iris cubes from the fetched data. 

Note that this is one person's personal library: I have no resources for support or extension beyond what is necessary for my own research. You are welcome to re-use any part of it (subject to the license, see below), but you would almost certainly be better advised to copy any bits you like and incoporate them into your own codebase than to rely on the stability of this.

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

The code in this library is licensed under the terms of the `GNU Lesser General Public License <https://www.gnu.org/licenses/lgpl.html>`_. The documentation under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_.

