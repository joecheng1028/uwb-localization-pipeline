import pytest
import sys
import os
import importlib
import json

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

traject_resample = importlib.import_module("4_traject_resample")

distance = traject_resample.distance
interpolate = traject_resample.interpolate
extract_meterwise_trajectory = traject_resample.extract_meterwise_trajectory


def test_distance():
    assert distance({"x": 1.0, "y": 2.0, "z": 3.0}, {"x": 4.0, "y": 6.0, "z": 3.0}) == pytest.approx(5)
    assert distance({"x": -1.0, "y": -2.0, "z": 0.0}, {"x": 2.0, "y": 2.0, "z": 0.0})== pytest.approx(5)
    assert distance({"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 0.0, "y": 0.0, "z": 0.0}) == pytest.approx(0)

def test_interpolate():
    assert interpolate({"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 1.0, "y": 1.0, "z": 1.0}, 0) == pytest.approx({"x":0.0, "y":0.0, "z":0.0})
    assert interpolate({"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 1.0, "y": 1.0, "z": 1.0}, 0.5) == pytest.approx({"x":0.5, "y":0.5, "z":0.5})
    assert interpolate({"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 1.0, "y": 1.0, "z": 1.0}, 1) == pytest.approx({"x": 1.0, "y": 1.0, "z": 1.0})
    assert interpolate({"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 1.0, "y": 1.0, "z": 1.0}, 2.0) == pytest.approx({"x":2, "y":2, "z":2})
    

def test_extract_meterwise_trajectory_output_exists(tmp_path):
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("x,y,z\n0.0,0.0,0.0\n2.0,0.0,0.0")
    output_json = tmp_path / "output.json"
    extract_meterwise_trajectory(input_csv, output_json, meter_step=1.0, offset={'x': 0, 'y': 0, 'z': 0})

    assert output_json.exists()

def test_extract_meterwise_trajectory_output_content(tmp_path):
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("x,y,z\n0.0,0.0,0.0\n2.0,0.0,0.0")
    output_json = tmp_path / "output.json"
    extract_meterwise_trajectory(input_csv, output_json, meter_step=1.0, offset={'x': 0, 'y': 0, 'z': 0})
    with open(output_json) as f:
        data = json.load(f)

    assert "trajectory" in data and len(data["trajectory"]) >= 2

def test_point_count(tmp_path):
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("x,y,z\n0.0,0.0,0.0\n5.0,0.0,0.0")
    output_json = tmp_path / "output.json"
    extract_meterwise_trajectory(input_csv, output_json, meter_step=1.0, offset={'x': 0, 'y': 0, 'z': 0})
    with open(output_json) as f:
        data = json.load(f)

    assert len(data["trajectory"]) == 6

def test_space(tmp_path):
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("x,y,z\n0.0,0.0,0.0\n5.0,0.0,0.0")
    output_json = tmp_path / "output.json"
    extract_meterwise_trajectory(input_csv, output_json, meter_step=1.0, offset={'x': 0, 'y': 0, 'z': 0})
    with open(output_json) as f:
        data = json.load(f)

    for i in range (1, len(data["trajectory"])):
        d = distance(data["trajectory"][i], data["trajectory"][i-1])
        assert d == pytest.approx(1.0)