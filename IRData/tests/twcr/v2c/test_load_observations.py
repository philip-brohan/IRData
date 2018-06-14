import unittest
from mock import patch

import IRData.twcr as twcr
import datetime
import sys
import os
import os.path
import shutil
import tempfile
import iris
import cf_units
import numpy
import pandas

version='2c'
 
# Can only load data if it's on disc - create fake data file
def fake_data_file(version,year,month,day,hour):
    file_name="%s/20CR/version_%s/observations/%04d/prepbufrobs_assim_%04d%02d%02d%02d.txt" % (
                 os.environ["SCRATCH"],
                 version,year,
                 year,month,day,hour)
    if os.path.isfile(file_name): return
    if not os.path.isdir(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    fh=open(file_name,'a')
    fh.close()

# Mock calls to pandas.read_fwf with a fake data.table constructor
def fake_prfwf(file_name,**kwargs): 
    year=int(os.path.basename(file_name)[18:22])
    month=int(os.path.basename(file_name)[22:24])
    day=int(os.path.basename(file_name)[24:26])
    hour=int(os.path.basename(file_name)[26:28])

    dtime=datetime.datetime(year,month,day,hour)
    offsets=numpy.linspace(-3,3,20)  
    uid=[]
    for idx in range(len(offsets)):
        dtt=dtime+datetime.timedelta(seconds=int(offsets[idx]*3600))
        uid.append("%04d%02d%02d%02dxxxxxxxxxx" % (
                   dtt.year,dtt.month,dtt.day,dtt.hour))
    dd={}
    for name in kwargs.get('names'):
        if name=='UID':
            dd[name]=uid
        else:
            dd[name]=uid
    fdf=pandas.DataFrame(data=dd)
    return fdf
    
class TestLoad(unittest.TestCase):
 
    # Controlled and temporary disc environment
    def setUp(self):
        self.oldscratch=os.environ["SCRATCH"]
        os.environ["SCRATCH"]=tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir("%s/20CR" % os.environ["SCRATCH"]):
            shutil.rmtree("%s/20CR" % os.environ["SCRATCH"])
        os.rmdir(os.environ["SCRATCH"])
        os.environ["SCRATCH"]=self.oldscratch

    # load obs for one file
    def test_load_1file(self):
        fake_data_file(version,1987,7,2,6)
        with patch.object(pandas,'read_fwf', 
                                side_effect=fake_prfwf) as mock_load: 
            o=twcr.load_observations_1file(
                                datetime.datetime(1987,7,2,6),
                                version=version)
        # Right dimensions
        self.assertEqual(len(o.UID),20)

    # load obs with weights
    def test_load_1file_weight(self):
        fake_data_file(version,1987,7,2,6)
        with patch.object(pandas,'read_fwf', 
                                side_effect=fake_prfwf) as mock_load: 
            o=twcr.load_observations_fortime(
                                datetime.datetime(1987,7,2,6),
                                version=version)
        # Right dimensions
        self.assertEqual(len(o.weight),20)
        # All equal to 1
        expected=numpy.repeat(1,20)
        self.assertTrue((o.weight == expected).all())

    # obs with weights and interpolation
    def test_load_1file_weight(self):
        fake_data_file(version,1987,7,2,6)
        fake_data_file(version,1987,7,2,12)
        with patch.object(pandas,'read_fwf', 
                                side_effect=fake_prfwf) as mock_load: 
            o=twcr.load_observations_fortime(
                                datetime.datetime(1987,7,2,7,30),
                                version=version)
        # Right dimensions
        self.assertEqual(len(o.weight),40)
        # Closer to 6 than 12
        expected=numpy.concatenate((numpy.repeat(0.75,20),
                                    numpy.repeat(0.25,20)))
        self.assertTrue((o.weight == expected).all())

    # load obs for a period
    def test_load_period(self):
        fake_data_file(version,1987,7,2,6)
        fake_data_file(version,1987,7,2,12)
        with patch.object(pandas,'read_fwf', 
                                side_effect=fake_prfwf) as mock_load: 
            o=twcr.load_observations(
                                datetime.datetime(1987,7,2,7),
                                datetime.datetime(1987,7,2,11),
                                version=version)
        # Right number in range
        self.assertEqual(len(o.UID),14)

    # Missing file
    def test_fetch_missing(self):
        with self.assertRaises(IOError) as cm:
            o=twcr.load_observations_1file(
                                datetime.datetime(1987,7,2,6),
                                version=version)
        self.assertIn("No obs file for given version and date",
                         str(cm.exception))
  
if __name__ == '__main__':
    unittest.main()
