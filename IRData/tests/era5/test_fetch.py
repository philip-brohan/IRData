import unittest
from unittest.mock import patch

import IRData.era5 as era5
import datetime
import ecmwfapi
import os
import shutil
import tempfile


class TestFetch(unittest.TestCase):

    # Controlled and temporary disc environment
    def setUp(self):
        self.oldscratch = os.environ["SCRATCH"]
        os.environ["SCRATCH"] = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir("%s/ERA5" % os.environ["SCRATCH"]):
            shutil.rmtree("%s/ERA5" % os.environ["SCRATCH"])
        os.rmdir(os.environ["SCRATCH"])
        os.environ["SCRATCH"] = self.oldscratch

    # basic analysis variable call
    def test_fetch_prmsl_enda(self):
        with patch.object(
            ecmwfapi.ECMWFDataServer, "retrieve", return_value=None
        ) as mock_method:
            era5.fetch("prmsl", datetime.datetime(2010, 3, 12), stream="enda")
        mock_method.assert_called_once_with(
            {
                "stream": "enda",
                "class": "ea",
                "format": "netcdf",
                "expver": "1",
                "levtype": "sfc",
                "dataset": "era5",
                "grid": "0.5/0.5",
                "number": "0/1/2/3/4/5/6/7/8/9",
                "date": "2010-03-01/to/2010-03-31",
                "target": "%s/ERA5/enda/hourly/2010/03/prmsl.nc" % os.getenv("SCRATCH"),
                "param": "msl",
                "time": "0/to/21/by/3",
                "type": "an",
            }
        )

    # oper stream variable call
    def test_fetch_prmsl_oper(self):
        with patch.object(
            ecmwfapi.ECMWFDataServer, "retrieve", return_value=None
        ) as mock_method:
            era5.fetch("prmsl", datetime.datetime(2010, 3, 12), stream="oper")
        mock_method.assert_called_once_with(
            {
                "dataset": "era5",
                "stream": "oper",
                "type": "an",
                "levtype": "sfc",
                "param": "msl",
                "grid": "0.25/0.25",
                "time": "0/to/23/by/1",
                "date": "2010-03-01/to/2010-03-31",
                "format": "netcdf",
                "target": "%s/ERA5/oper/hourly/2010/03/prmsl.nc" % os.getenv("SCRATCH"),
            }
        )

    # basic forecast variable call
    def test_fetch_prate(self):
        with patch.object(
            ecmwfapi.ECMWFDataServer, "retrieve", return_value=None
        ) as mock_method:
            era5.fetch("prate", datetime.datetime(2010, 3, 12), stream="enda")
        for start_hour in (6, 18):
            mock_method.assert_any_call(
                {
                    "class": "ea",
                    "dataset": "era5",
                    "date": "2010-03-01/to/2010-03-31",
                    "expver": "1",
                    "levtype": "sfc",
                    "number": "0/1/2/3/4/5/6/7/8/9",
                    "param": "tp",
                    "stream": "enda",
                    "time": "%02d" % start_hour,
                    "step": "0/to/18/by/3",
                    "type": "fc",
                    "grid": "0.5/0.5",
                    "format": "netcdf",
                    "target": "%s/ERA5/enda/hourly/2010/03/prate.%02d.nc"
                    % (os.getenv("SCRATCH"), start_hour),
                }
            )

    # Special case for end of month
    def test_fetch_prmsl_eom(self):
        with patch.object(
            ecmwfapi.ECMWFDataServer, "retrieve", return_value=None
        ) as mock_method:
            era5.fetch("prmsl", datetime.datetime(2010, 3, 31, 23, 30), stream="enda")
        mock_method.assert_called_with(
            {
                "class": "ea",
                "dataset": "era5",
                "date": "2010-03-01/to/2010-03-31",
                "expver": "1",
                "levtype": "sfc",
                "number": "0/1/2/3/4/5/6/7/8/9",
                "param": "msl",
                "stream": "enda",
                "time": "0/to/21/by/3",
                "type": "an",
                "grid": "0.5/0.5",
                "format": "netcdf",
                "target": "%s/ERA5/enda/hourly/2010/03/prmsl.nc" % os.getenv("SCRATCH"),
            }
        )
        mock_method.assert_any_call(
            {
                "class": "ea",
                "dataset": "era5",
                "date": "2010-04-01/to/2010-04-30",
                "expver": "1",
                "levtype": "sfc",
                "number": "0/1/2/3/4/5/6/7/8/9",
                "param": "msl",
                "stream": "enda",
                "time": "0/to/21/by/3",
                "type": "an",
                "grid": "0.5/0.5",
                "format": "netcdf",
                "target": "%s/ERA5/enda/hourly/2010/04/prmsl.nc" % os.getenv("SCRATCH"),
            }
        )

    # Dud variable
    def test_fetch_mslp(self):
        with self.assertRaises(Exception) as cm:
            era5.fetch("mslp", datetime.datetime(2010, 3, 12))
        self.assertEqual("Unsupported variable mslp", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
