import unittest
from mock import patch

import IRData.era5 as era5
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
        if os.path.isdir("%s/ERA5" % os.environ["SCRATCH"]):
            shutil.rmtree("%s/ERA5" % os.environ["SCRATCH"])
        os.rmdir(os.environ["SCRATCH"])
        os.environ["SCRATCH"]=self.oldscratch

    # basic analysis variable call
    def test_fetch_prmsl_enda(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            era5.fetch('prmsl',
                       datetime.datetime(2010,3,12),
                       stream='enda')
        mock_method.assert_called_once_with(
                {'stream' : 'enda', 
                 'format' : 'netcdf',
                 'levtype': 'sfc', 
                 'dataset': 'era5',
                 'grid'   : '0.5/0.5',
                 'date'   : '2010-03-01/to/2010-03-31',
                 'target' : '%s/ERA5/enda/hourly/2010/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param'  : 'msl',
                 'time'   : '0/to/23/by/1',
                 'type'   : 'an'})

    # oper stream variable call
    def test_fetch_prmsl_oper(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            era5.fetch('prmsl',
                       datetime.datetime(2010,3,12),
                       stream='oper')
        mock_method.assert_called_once_with(
                {'stream' : 'oper', 
                 'format' : 'netcdf',
                 'levtype': 'sfc', 
                 'dataset': 'era5',
                 'grid'   : '0.25/0.25',
                 'date'   : '2010-03-01/to/2010-03-31',
                 'target' : '%s/ERA5/oper/hourly/2010/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param'  : 'msl',
                 'time'   : '0/to/23/by/1',
                 'type'   : 'an'})

    # basic forecast variable call
    def test_fetch_prate(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            era5.fetch('prate',
                       datetime.datetime(2010,3,12),
                       stream='enda')
        for start_hour in (6,18):
            mock_method.assert_any_call(
               {'dataset'   : 'era5',
                'stream'    : 'enda',
                'type'      : 'fc',
                'levtype'   : 'sfc',
                'param'     : 'tp',
                'grid'      : '0.5/0.5',
                'time'      : "%02d" % start_hour,
                'step'      : '0/to/18/by/1',
                'date'      : '2010-03-01/to/2010-03-31',
                'format'    : 'netcdf',
                'target'    : '%s/ERA5/enda/hourly/2010/03/prate.%02d.nc' % \
                                 (os.getenv('SCRATCH'),start_hour)})

    # Special case for end of month
    def test_fetch_prmsl_eom(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            era5.fetch('prmsl',
                       datetime.datetime(2010,3,31,23,30),
                       stream='enda')
        mock_method.assert_called_with(
                {'stream' : 'enda', 
                 'format' : 'netcdf',
                 'levtype': 'sfc', 
                 'dataset': 'era5',
                 'grid'   : '0.5/0.5',
                 'date'   : '2010-03-01/to/2010-03-31',
                 'target' : '%s/ERA5/enda/hourly/2010/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param'  : 'msl',
                 'time'   : '0/to/23/by/1',
                 'type'   : 'an'})
        mock_method.assert_any_call(
                {'stream' : 'enda', 
                 'format' : 'netcdf',
                 'levtype': 'sfc', 
                 'dataset': 'era5',
                 'grid'   : '0.5/0.5',
                 'date'   : '2010-04-01/to/2010-04-30',
                 'target' : '%s/ERA5/enda/hourly/2010/04/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param'  : 'msl',
                 'time'   : '0/to/23/by/1',
                 'type'   : 'an'})

    # Dud variable
    def test_fetch_mslp(self):
        with self.assertRaises(StandardError) as cm:
            era5.fetch('mslp',
                          datetime.datetime(2010,3,12))
        self.assertEqual("Unsupported variable mslp",
                         str(cm.exception))
 
if __name__ == '__main__':
    unittest.main()
