Installation
============

Known to work on with Python 2.7 on modern Linux and OS X systems. Not tested on anything else.

One environment variable must be set:

* SCRATCH - the name of a directory to download weather data to.

Relies on `Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_, so first install that.
Uses the ECMWF api: `ecmwfapi <https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets>`_ - to download CERA-20C or ERA5 data. Follow the instructions on that page to get an ECMWF api account (free).

Then install the package from the source in `<https://github.com/philip-brohan/OWData>`_:

* Install with 'python setup.py install --user'.
* Test with 'python setup.py test'.

