import pandas as pd
import pytest
import sys
import os
import importlib

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

compute_metrics_from_columns = importlib.import_module("8_position_accuracy").compute_metrics_from_columns

@pytest.fixture
def df_test1():
    return pd.DataFrame([
            [0.0, 0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0, 2.0],
        ], columns=["x_true_col", "y_true_col", "x_est_col", "y_est_col"]
    )

@pytest.fixture
def df_test2():
    return pd.DataFrame([
            [0.0, 0.0, 3.0, 4.0],
            [1.0, 1.0, 4.0, 5.0],
            [2.0, 2.0, 5.0, 6.0],
        ], columns=["x_true_col", "y_true_col", "x_est_col", "y_est_col"]
    )

def test_compute_stats_allZero(df_test1):
    result = compute_metrics_from_columns(df_test1,"x_true_col", "y_true_col", "x_est_col", "y_est_col")
    dict1 = pytest.approx({
        'count': 3,
        'σ_x': 0,
        'σ_y':0,
        'mean_abs_dx': 0,
        'mean_abs_dy': 0,
        'error_min': 0,
        'error_max': 0,
        'error_mean': 0,
        'error_median': 0,
        'error_std': 0,
        'RMSE': 0,
        'DRMS': 0,
        '2DRMS': 0,
        'CEP50': 0,
        'R95': 0,
        '2D Precision (σ₂D)': 0
    })
    assert result == dict1

def test_compute_stats_distanceIs5(df_test2):
    result = compute_metrics_from_columns(df_test2,"x_true_col", "y_true_col", "x_est_col", "y_est_col")
    dict2 = pytest.approx({
        'count': 3,
        'σ_x': 0,
        'σ_y':0,
        'mean_abs_dx': 3,
        'mean_abs_dy': 4,
        'error_min': 5,
        'error_max': 5,
        'error_mean': 5,
        'error_median': 5,
        'error_std': 0,
        'RMSE': 5,
        'DRMS': 0,
        '2DRMS': 0,
        'CEP50': 5,
        'R95': 5,
        '2D Precision (σ₂D)': 5
    })
    assert result == dict2