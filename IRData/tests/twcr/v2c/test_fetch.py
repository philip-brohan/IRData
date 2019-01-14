import unittest
from unittest.mock import patch

import IRData.twcr as twcr
import datetime
import subprocess
import zipfile
import os
import shutil
import tempfile
 
version='2c'

class TestFetch(unittest.TestCase):
 
    # Controlled and temporary disc environment
    def setUp(self):
        self.oldscratch=os.environ["SCRATCH"]
        os.environ["SCRATCH"]=tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir("%s/20CR" % os.environ["SCRATCH"]):
            shutil.rmtree("%s/20CR" % os.environ["SCRATCH"])
        os.rmdir(os.environ["SCRATCH"])
        os.environ["SCRATCH"]=self.oldscratch

    # basic call
    def test_fetch_prmsl(self):
        with patch.object(subprocess, 'call', 
                                return_value=0) as mock_method: 
            twcr.fetch('prmsl',
                       datetime.datetime(1969,3,12),
                       version=version)
        remote_dir=("http://portal.nersc.gov/project/20C_Reanalysis/"+
                        "20C_Reanalysis_version2c_ensemble/")
        remote_file="%s/analysis/prmsl/prmsl_1969.nc" % remote_dir
        local_dir="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
        local_file="%s/1969/prmsl.nc" % local_dir
        mock_method.assert_called_once_with(
                  "wget -O %s %s"  % (local_file,remote_file),
                  shell=True)

    # special case for end of year
    def test_fetch_prmsl_eol(self):
        local_dir="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
        remote_dir=("http://portal.nersc.gov/project/20C_Reanalysis/"+
                        "20C_Reanalysis_version2c_ensemble/")
        with patch.object(subprocess, 'call', 
                                return_value=0) as mock_method: 
            twcr.fetch('prmsl',
                       datetime.datetime(1969,12,31,22),
                       version=version)
        remote_file="%s/analysis/prmsl/prmsl_1969.nc" % remote_dir
        local_file="%s/1969/prmsl.nc" % local_dir
        mock_method.assert_called_with(
                  "wget -O %s %s"  % (local_file,remote_file),
                  shell=True)
        remote_file="%s/analysis/prmsl/prmsl_1970.nc" % remote_dir
        local_file="%s/1970/prmsl.nc" % local_dir
        mock_method.assert_any_call(
                  "wget -O %s %s"  % (local_file,remote_file),
                  shell=True)

    # Dud variable
    def test_fetch_mslp(self):
        with self.assertRaises(Exception) as cm:
            twcr.fetch('mslp',
                       datetime.datetime(1969,3,12),
                       version=version)
        self.assertEqual("Unsupported variable mslp",
                         str(cm.exception))

    # observations
    def test_fetch_observations(self):
        remote_file=("http://portal.nersc.gov/project/m958/2c_observations/"+
                    "1969.zip")
        local_dir="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
        os.makedirs("%s/observations" % local_dir)
        local_file="%s/observations/1969.zip" % local_dir
        # First try - just the download - unzip will fail
        with patch.object(subprocess, 'call', 
                                return_value=0) as mock_get: 
            with self.assertRaises(IOError) as cm:
                twcr.fetch_observations(datetime.datetime(1969,3,12),
                                        version=version)
        mock_get.assert_called_once_with(
                  "wget -O %s %s"  % (local_file,remote_file),
                  shell=True)
        # Make a fake zip file (so no download) and test the unzip
        tzf=zipfile.ZipFile(local_file,'w')
        tzf.close()
        with patch.object(zipfile.ZipFile, 'extractall', 
                                return_value=None) as mock_unzip:
            twcr.fetch_observations(datetime.datetime(1969,3,12),
                                    version=version)
        mock_unzip.assert_called_once_with("%s/observations/" %
                                           local_dir)

 
if __name__ == '__main__':
    unittest.main()
