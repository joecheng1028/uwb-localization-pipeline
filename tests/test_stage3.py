import pandas as pd
import pytest
import sys
import os
import importlib

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

sync_shift_to_uwb = importlib.import_module("3_sync_shift_to_uwb")

shift_uwb_origin = sync_shift_to_uwb.shift_uwb_origin
sync_odom_to_uwb = sync_shift_to_uwb.sync_odom_to_uwb

@pytest.fixture
def df_stage3_uwb():
    return pd.DataFrame([
            [1753339740.09, 0.00, 2.0, 3.0, 4.0, 10.0, 12.0, 14.0, 15.0],
            [1753339740.29, 1.0,  2.5, 3.5, 4.2, 12.0, 12.0, 63.0, 21.0],
            [1753339740.59, 2.0,  2.8, 3.8, 4.4, 12.0, 12.0, 63.0, 21.0],
            [1753339740.79, 3.0,  1.2, 2.1, 3.3, 11.0, 13.0, 17.0, 19.0],
            [1753339741.08, 4.0,  0.5, 1.7, 2.9,  9.0,  8.0,  6.0,  5.0],
        ], columns=["timestamp_abs (s)", "timestamp_norm (s)", "x", "y", "z", "qx", "qy", "qz", "qw"]
    )

@pytest.fixture
def df_stage3_odom():
    return pd.DataFrame([
            [1753339740.09, 0.52, 2.0, 3.0, 4.0, 10.0, 12.0, 14.0, 15.0],
            [1753339740.29, 0.76, 2.5, 3.5, 4.2, 12.0, 12.0, 63.0, 21.0],
            [1753339740.59, 1.35, 2.8, 3.8, 4.4, 12.0, 12.0, 63.0, 21.0],
            [1753339740.79, 1.76, 1.2, 2.1, 3.3, 11.0, 13.0, 17.0, 19.0],
            [1753339741.08, 2.25, 0.5, 1.7, 2.9,  9.0,  8.0,  6.0,  5.0],
            [1753339741.29, 2.87, 3.6, 2.2, 1.1,  7.0, 14.0, 22.0, 18.0],
            [1753339741.58, 3.32, 4.1, 3.3, 2.5, 16.0, 11.0,  9.0, 13.0],
            [1753339741.73, 3.49, 2.9, 4.5, 3.7, 20.0, 18.0, 25.0, 30.0],
            [1753339742.29, 4.61, 3.2, 1.4, 2.8, 13.0, 15.0, 17.0, 21.0],
        ], columns=["timestamp_abs (s)", "timestamp_norm (s)", "x", "y", "z", "qx", "qy", "qz", "qw"]
    )

def test_shift_length(df_stage3_uwb):
    test_result = shift_uwb_origin(df_stage3_uwb)
    assert len(test_result) == len(df_stage3_uwb) - 1

def test_shift_first_row(df_stage3_uwb):
    test_result = shift_uwb_origin(df_stage3_uwb)
    assert (test_result.iloc[0][["x_shifted","y_shifted"]] == 0).all()

def test_shift_reduction(df_stage3_uwb):
    test_result = shift_uwb_origin(df_stage3_uwb)
    x0, y0 = 2.5, 3.5
    assert ((test_result["x"] - test_result["x_shifted"]) - x0).abs().max() < 1e-6
    assert ((test_result["y"] - test_result["y_shifted"]) - y0).abs().max() < 1e-6

def test_sync_length(df_stage3_uwb, df_stage3_odom):

    test_result = sync_odom_to_uwb(df_stage3_uwb, df_stage3_odom, 0.5)
    assert len(test_result) <= len(df_stage3_odom)

def test_sync_timestamp(df_stage3_uwb, df_stage3_odom):
    """result["timestamp_norm (s)"] matches the 3 matched UWB timestamps [1.0, 2.0, 3.0]"""

    test_result = sync_odom_to_uwb(df_stage3_uwb, df_stage3_odom, 0.5)
    assert list(test_result["timestamp_norm (s)"]) == [1.0, 2.0, 3.0]


def test_sync_lookup(df_stage3_uwb, df_stage3_odom):
    """Each matched odom row exists in df_stage3_odom — check column by column"""

    test_result = sync_odom_to_uwb(df_stage3_uwb, df_stage3_odom, 0.5)
    cols = ["timestamp_abs (s)", "x", "y", "z", "qx", "qy", "qz", "qw"]
    merged = test_result[cols].merge(df_stage3_odom[cols], on=cols, how="inner")
    assert len(merged) == len(test_result)