import importlib
import os
import sys
import pytest

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

axis_shift = importlib.import_module("5_traject_voxel_shift").axis_shift


def test_axis_shift():
    assert axis_shift({"x": 1.0, "y": 2.0, "z": 3.0}, 0.0, 0.0, 0.0) == pytest.approx({"x":1.0, "y": -3.0, "z": 2.0})
    assert axis_shift({"x": 5.0, "y": 6.0, "z": 7.0}, 5.0, 6.0, 7.0) == pytest.approx({"x":0.0, "y": 0.0, "z": 0.0})