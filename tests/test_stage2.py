import pandas as pd
import pandas as _pd
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib
import csv


odom_clean = importlib.import_module("2_odom_clean")
filter_zero_xyz_rows = odom_clean.filter_zero_xyz_rows
remove_zero_xyz_rows = odom_clean.remove_zero_xyz_rows

def test_length(sample_stage2):
    test_result = filter_zero_xyz_rows(sample_stage2)
    assert len(test_result)== 8

def test_all_non_zero(sample_stage2):
    # "not all elements are zero" for all row
    test_result = filter_zero_xyz_rows(sample_stage2)
    assert (test_result[["x","y","z"]] != 0).any(axis=1).all()

def test_expected(sample_stage2):
    test_result = filter_zero_xyz_rows(sample_stage2)
    pd.testing.assert_frame_equal(test_result, sample_stage2.loc[[1,2,3,4,5,6,7,9]])

def test_mock_exists(mocker):
    mocker.patch("2_odom_clean.os.path.exists", return_value=False)
    remove_zero_xyz_rows()
    # function exits early, no file written — just verify it didn't crash

    assert remove_zero_xyz_rows() is None