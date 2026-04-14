# tests/test_fixtures_parametrize.py
import pytest
import pandas as pd
import numpy as np

# --- Fixture usage ---

def test_df_shape(sample_odom_df):
    assert sample_odom_df.shape == (5, 4)

def test_df_columns(sample_odom_df): # no Parametrization
    assert list(sample_odom_df.columns) == ["timestamp", "x", "y", "z"]

def test_df_no_nulls(sample_odom_df):
    assert sample_odom_df.isnull().sum().sum() == 0

# --- tmp_path built-in fixture ---

def test_write_and_read_csv(tmp_path, sample_odom_df):
    filepath = tmp_path / "test_output.csv"
    sample_odom_df.to_csv(filepath, index=False)
    loaded = pd.read_csv(filepath)
    assert loaded.shape == sample_odom_df.shape

# --- Parametrize ---

@pytest.mark.parametrize("value,expected", [
    (4.0,  2.0),
    (9.0,  3.0),
    (0.0,  0.0),
    (1.0,  1.0),
    (16.0, 4.0),
])
def test_sqrt(value, expected):
    assert np.sqrt(value) == pytest.approx(expected)


@pytest.mark.parametrize("row_count,col_count", [
    (5, 4),
    (10, 4),
    (0, 4),
])
def test_df_row_count(row_count, col_count):
    df = pd.DataFrame(np.zeros((row_count, col_count)),
                      columns=["timestamp", "x", "y", "z"])
    assert df.shape == (row_count, col_count)

@pytest.mark.parametrize("header", [
    "timestamp", "x_uwb", "y_uwb",
])
def test_check_header(sample_uwb_df, header):
    assert header in sample_uwb_df.columns

@pytest.mark.parametrize("check, lower, upper",
    [("x_uwb", 0, 5), ("y_uwb", 0, 5)]
)
def test_range_check(sample_uwb_df, check, lower, upper):
    assert sample_uwb_df[check].between(lower, upper).all()


def test_timestamp(sample_uwb_df):
    assert sample_uwb_df["timestamp"].is_monotonic_increasing
    diffs = sample_uwb_df["timestamp"].diff().dropna()
    assert diffs.between(0.20, 0.30).all()
