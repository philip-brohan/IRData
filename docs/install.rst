Installation
============

Known to work on with Python 3.6 on modern Linux and OS X systems. Not tested on anything else.

One environment variable must be set:

* SCRATCH - the name of a directory to download weather data to.

Relies on `Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_, so first `install that <https://scitools.org.uk/iris/docs/latest/installing.html>`_.

Uses the ECMWF api: `ecmwfapi <https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets>`_ - to download CERA-20C and ERA5 data. Follow the instructions on that page to get an ECMWF api account (free). You don't have to install the package (setup will do that - see below), but you do need to an api key. If you are only using 20CR data you can skip this step.

Then download or fork the source in `<https://github.com/philip-brohan/IRData>`_:

* Install with 'python setup.py install --user'.
* Test with 'python setup.py test'.

