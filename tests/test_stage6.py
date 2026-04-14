import pytest
import pandas as pd
import os
import sys
import json
from unittest.mock import patch
import importlib


# def test_something():
#     with patch("module_name.VARIABLE_NAME", {"key": "value"}):
#         # inside this block, module_name.VARIABLE_NAME is your fake dict
#         ...
#     # after the block, original value is restored


script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

error_kdtree = importlib.import_module("6_error_kdtree")
compute_error_and_save = error_kdtree.compute_error_and_save

def test_compute_error_and_save_output_exists(tmp_path):
    # Create pose CSV
    pose_df = pd.DataFrame({
        "timestamp_norm (s)": [0.002, 0.004, 0.006, 0.008, 0.010],
        "x": [2.0, 3.0, 4.0, 5.0, 6.0],
        "y": [0.0, 1.0, 2.0, 3.0, 4.0],
    })
    pose_csv = tmp_path / "pose.csv"
    pose_df.to_csv(pose_csv, index=False)

    # Create UWB CSV
    uwb_df = pd.DataFrame({
        "timestamp_norm (s)": [0.002, 0.004, 0.006, 0.008, 0.010],
        "x_shifted": [2.7, 3.4, 4.3, 5.8, 6.6],
        "y_shifted": [0.9, 1.6, 2.2, 3.6, 4.3],
    })
    uwb_csv = tmp_path / "uwb.csv"
    uwb_df.to_csv(uwb_csv, index=False)
    # Create voxel JSON
    # voxel_json — list of dicts with "trajPoint": {"x", "y"} and "voxel": {"value"}
    voxel_data = [
        {"trajPoint": {"x": 1.9, "y": 0.6}, "voxel": {"value": 0.52}},
        {"trajPoint": {"x": 2.4, "y": 1.4}, "voxel": {"value": 1.57}},
        {"trajPoint": {"x": 3.0, "y": 2.6}, "voxel": {"value": 0.64}},
        {"trajPoint": {"x": 4.6, "y": 3.9}, "voxel": {"value": 0.35}},
        {"trajPoint": {"x": 5.8, "y": 4.2}, "voxel": {"value": 1.44}},
    ]
    voxel_json = "5_odom_converted.json"
    with open(tmp_path / "5_odom_converted.json", "w") as f:
        json.dump(voxel_data, f)

    # Define fake lookups
    fake_pose_file_lookup = {"odom": str(pose_csv)}
    fake_pose_suffix_lookup = {"odom": ""}

    # path safeguard part 1
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    # Call function
    compute_error_and_save(voxel_json, "odom", uwb_csv, fake_pose_file_lookup, fake_pose_suffix_lookup)

    # path safeguard part 2
    os.chdir(original_dir)

    # Assert output exists
    output_path = tmp_path / "6_odom_converted_error.csv"
    assert output_path.exists()

def test_compute_error_and_save_output_content(tmp_path):
    # Create pose CSV
    pose_df = pd.DataFrame({
        "timestamp_norm (s)": [0.002, 0.004, 0.006, 0.008, 0.010],
        "x": [2.0, 3.0, 4.0, 5.0, 6.0],
        "y": [0.0, 1.0, 2.0, 3.0, 4.0],
    })
    pose_csv = tmp_path / "pose.csv"
    pose_df.to_csv(pose_csv, index=False)

    # Create UWB CSV
    uwb_df = pd.DataFrame({
        "timestamp_norm (s)": [0.002, 0.004, 0.006, 0.008, 0.010],
        "x_shifted": [2.7, 3.4, 4.3, 5.8, 6.6],
        "y_shifted": [0.9, 1.6, 2.2, 3.6, 4.3],
    })
    uwb_csv = tmp_path / "uwb.csv"
    uwb_df.to_csv(uwb_csv, index=False)
    # Create voxel JSON
    # voxel_json — list of dicts with "trajPoint": {"x", "y"} and "voxel": {"value"}
    voxel_data = [
        {"trajPoint": {"x": 1.9, "y": 0.6}, "voxel": {"value": 0.52}},
        {"trajPoint": {"x": 2.4, "y": 1.4}, "voxel": {"value": 1.57}},
        {"trajPoint": {"x": 3.0, "y": 2.6}, "voxel": {"value": 0.64}},
        {"trajPoint": {"x": 4.6, "y": 3.9}, "voxel": {"value": 0.35}},
        {"trajPoint": {"x": 5.8, "y": 4.2}, "voxel": {"value": 1.44}},
    ]
    voxel_json = "5_odom_converted.json"
    with open(tmp_path / "5_odom_converted.json", "w") as f:
        json.dump(voxel_data, f)

    # Define fake lookups
    fake_pose_file_lookup = {"odom": str(pose_csv)}
    fake_pose_suffix_lookup = {"odom": ""}

    # path safeguard part 1
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    
    # Call function
    compute_error_and_save(voxel_json, "odom", uwb_csv, fake_pose_file_lookup, fake_pose_suffix_lookup)

    # path safeguard part 2
    os.chdir(original_dir)

    # Load .csv
    with open(tmp_path / "6_odom_converted_error.csv") as f:
        data = pd.read_csv(f)

    # Assert output content
    assert "timestamp_norm (s)" in data.columns and "x_uwb" in data and "y_uwb" in data and "error_xy" in data and "voxel_value" in data
    assert len(data) == 5