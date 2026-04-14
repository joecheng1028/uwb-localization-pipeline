import pytest
import os
import sys
import importlib

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

plot_regression = importlib.import_module("7d_plot_regressions")
exp_model = plot_regression.exp_model
sturges_bins = plot_regression.sturges_bins

def test_sturges_bins_simple():
    assert sturges_bins(1) == 1
    assert sturges_bins(8) == 4

def test_sturges_bins_abnormale():
    assert sturges_bins(0) == 1
    assert sturges_bins(-255) == 1

def test_sturges_bins_irregular():
    assert sturges_bins(50) == 7

def test_exp_model_x_isZero():
    assert exp_model(0, 2, 3, 4) == pytest.approx(4)
    assert exp_model(0, -2, 25, 0) == pytest.approx(0)
    assert exp_model (0, 34, -10, 38) == pytest.approx(38)

def test_exp_model_regular():
    assert exp_model(3, 2, 3, 4) == pytest.approx(5.99975318)
    assert exp_model(2, -2, 25, 0) == pytest.approx(-2)
    assert exp_model (5, 34, 10, 38) == pytest.approx(72)