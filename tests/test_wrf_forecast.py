from datetime import datetime, timedelta
from glob import glob
import os

from numpy.testing import assert_almost_equal
import pytest
import xarray as xr


from spt_compute import run_lsm_forecast_process

from .conftest import RAPID_EXE_PATH, SetupForecast


@pytest.fixture(scope="module")
def wrf_setup(request, tclean):
    return SetupForecast(tclean, "m-s", "wrf")

def test_wrf_forecast(wrf_setup):
    """
    Test basic WRF forecast process.
    """
    qout_name = 'Qout_wrf_wrf_1hr_20080601to20080601.nc'
    out_forecast_folder = '20080601t01'
    watershed = 'm-s'

    start_datetime = datetime.utcnow()
    run_lsm_forecast_process(rapid_executable_location=RAPID_EXE_PATH,
                             rapid_io_files_location=wrf_setup.rapid_io_folder,
                             lsm_forecast_location=wrf_setup.lsm_folder,
                             main_log_directory=wrf_setup.log_folder,
                             timedelta_between_forecasts=timedelta(seconds=0))

    output_folder = os.path.join(wrf_setup.rapid_io_folder, 'output', watershed, out_forecast_folder)
    # check log file exists
    log_files = glob(os.path.join(wrf_setup.log_folder,
                                  "spt_compute_lsm_{0:%y%m%d%H%M}*.log".format(start_datetime)))
    assert len(log_files) == 1
    # check Qout file
    qout_file = os.path.join(output_folder, qout_name)
    assert os.path.exists(qout_file)

    compare_qout_file = os.path.join(wrf_setup.watershed_compare_folder, out_forecast_folder, qout_name)
    with xr.open_dataset(qout_file) as xqf, \
            xr.open_dataset(compare_qout_file) as xqc:
        print(xqf)
        assert_almost_equal()
        assert_almost_equal(xqf.Qout.values, xqc.Qout.values)
        assert_almost_equal(xqf.lat.values, xqc.lat.values)
        assert_almost_equal(xqf.lon.values, xqc.lon.values)

    # make sure no m3 file exists
    m3_files = glob(os.path.join(output_folder, "m3_riv*.nc"))
    assert len(m3_files) == 0
    # check Qinit file
    assert os.path.exists(os.path.join(wrf_setup.watershed_input_folder, 'Qinit_20080601t01.csv'))

