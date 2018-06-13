import unittest
from mock import patch

import IRData.cera20c as cera20c
import datetime
import ecmwfapi
import os
import shutil
import tempfile
 
class TestFetch(unittest.TestCase):
 
    # Controlled and temporary disc environment
    def setUp(self):
        self.oldscratch=os.environ["SCRATCH"]
        os.environ["SCRATCH"]=tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir("%s/CERA_20C" % os.environ["SCRATCH"]):
            shutil.rmtree("%s/CERA_20C" % os.environ["SCRATCH"])
        os.rmdir(os.environ["SCRATCH"])
        os.environ["SCRATCH"]=self.oldscratch

    # basic analysis variable call
    def test_fetch_prmsl(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            cera20c.fetch('prmsl',
                          datetime.datetime(1969,3,12))
        mock_method.assert_called_once_with(
                {'stream': 'enda', 
                 'format': 'netcdf',
                 'levtype': 'sfc', 
                 'number': '0/1/2/3/4/5/6/7/8/9',
                 'dataset': 'cera20c',
                 'grid': '1.25/1.25',
                 'expver': '1',
                 'date': '1969-03-01/to/1969-03-31',
                 'class': 'ep',
                 'target': '%s/CERA_20C/hourly/1969/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param': 'mslp',
                 'time': '00/03/06/09/12/15/18/21',
                 'type': 'an'})

    # basic forecast variable call
    def test_fetch_prate(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            cera20c.fetch('prate',
                          datetime.datetime(1969,3,12))
        mock_method.assert_called_with(
                {'dataset'   : 'cera20c',
                 'stream'    : 'enda',
                 'type'      : 'fc',
                 'class'     : 'ep',
                 'expver'    : '1',
                 'levtype'   : 'sfc',
                 'param'     : 'tp',
                 'time'      : '18',
                 'step'      : '27',
                 'grid'      : '1.25/1.25',
                 'number'    : '0/1/2/3/4/5/6/7/8/9',
                 'date'      : "1969-03-01/to/1969-03-31",
                 'format'    : 'netcdf',
                 'target'    : '%s/CERA_20C/hourly/1969/03/prate.p1d.nc' % \
                                 os.getenv('SCRATCH')})
        mock_method.assert_any_call(
                {'dataset'   : 'cera20c',
                 'stream'    : 'enda',
                 'type'      : 'fc',
                 'class'     : 'ep',
                 'expver'    : '1',
                 'levtype'   : 'sfc',
                 'param'     : 'tp',
                 'time'      : '18',
                 'step'      : '3/6/9/12/15/18/21/24',
                 'grid'      : '1.25/1.25',
                 'number'    : '0/1/2/3/4/5/6/7/8/9',
                 'date'      : "1969-03-01/to/1969-03-31",
                 'format'    : 'netcdf',
                 'target'    : '%s/CERA_20C/hourly/1969/03/prate.nc' % \
                                 os.getenv('SCRATCH')})

    # Special case for end of month
    def test_fetch_prmsl_eom(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            cera20c.fetch('prmsl',
                          datetime.datetime(1969,3,31,21))
        mock_method.assert_called_with(
                {'stream': 'enda', 
                 'format': 'netcdf',
                 'levtype': 'sfc', 
                 'number': '0/1/2/3/4/5/6/7/8/9',
                 'dataset': 'cera20c',
                 'grid': '1.25/1.25',
                 'expver': '1',
                 'date': '1969-03-01/to/1969-03-31',
                 'class': 'ep',
                 'target': '%s/CERA_20C/hourly/1969/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param': 'mslp',
                 'time': '00/03/06/09/12/15/18/21',
                 'type': 'an'})
        mock_method.assert_any_call(
                {'stream': 'enda', 
                 'format': 'netcdf',
                 'levtype': 'sfc', 
                 'number': '0/1/2/3/4/5/6/7/8/9',
                 'dataset': 'cera20c',
                 'grid': '1.25/1.25',
                 'expver': '1',
                 'date': '1969-04-01/to/1969-04-30',
                 'class': 'ep',
                 'target': '%s/CERA_20C/hourly/1969/04/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param': 'mslp',
                 'time': '00/03/06/09/12/15/18/21',
                 'type': 'an'})

    # Dud variable
    def test_fetch_mslp(self):
        with self.assertRaises(StandardError) as cm:
            cera20c.fetch('mslp',
                          datetime.datetime(1969,3,12))
        self.assertEqual("Unsupported variable mslp",
                         str(cm.exception))
 
if __name__ == '__main__':
    unittest.main()
