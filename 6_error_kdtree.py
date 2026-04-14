"""
Spatially matches voxel reliability scores to pose estimates using KDTree, then computes UWB positioning error.
"""
import os
import pandas as pd
import numpy as np
import json
from scipy.spatial import KDTree
import yaml
import argparse

def compute_error_and_save(voxel_json_path, pose_key, uwb_csv, POSE_FILE_LOOKUP, POSE_SUFFIX_LOOKUP):
    """
    Extract data from input, and performs KDTree built on trajectory point and query with position data

    Args:
        voxel_json_path (str):  All .json in the directory that matches with keyword
        pose_key (str):         Robot data input (either amcl or odom (default))
        uwb_csv (str):          Path to UWB reference CSV file

    Returns: Nothing
    """
    pose_suffix = POSE_SUFFIX_LOOKUP[pose_key]
    pose_csv = POSE_FILE_LOOKUP[pose_key]

    basename = os.path.splitext(voxel_json_path)[0]
    if basename.startswith("5_"):
        new_base = "6_" + basename[2:]
    else:
        new_base = basename
    output_csv = new_base + "_error.csv"

    print(f"\nProcessing: {voxel_json_path} -> {output_csv}")

    # Input files are loaded
    uwb_df = pd.read_csv(uwb_csv)
    pose_df = pd.read_csv(pose_csv)
    with open(voxel_json_path) as f:
        voxel_data = json.load(f)

    # Trajectory points and voxel values are extracted
    traj_xy = np.array([[d["trajPoint"]["x"], d["trajPoint"]["y"]] for d in voxel_data])
    voxel_values = np.array([d["voxel"]["value"] for d in voxel_data])

    # Column names are checked for consistency before merge
    x_col_pre = f"x{pose_suffix}" if f"x{pose_suffix}" in pose_df.columns else "x"
    y_col_pre = f"y{pose_suffix}" if f"y{pose_suffix}" in pose_df.columns else "y"

    # Pose points are prepared for nearest-neighbor search
    pose_points = pose_df[[x_col_pre, y_col_pre]].copy()
    pose_xy = pose_points.to_numpy()

    # KDTree is built on trajectory points and queried with pose points
    tree = KDTree(traj_xy)
    _, indices = tree.query(pose_xy)
    pose_df["voxel_value"] = voxel_values[indices]

    # Data is merged with UWB reference using timestamps
    merged_df = pd.merge(pose_df, uwb_df, on="timestamp_norm (s)", suffixes=(pose_suffix, '_uwb'))

    # Column names are resolved after merge
    x_col_post = f"{x_col_pre}{pose_suffix}" if x_col_pre == "x" else x_col_pre
    y_col_post = f"{y_col_pre}{pose_suffix}" if y_col_pre == "y" else y_col_pre

    # UWB shifted coordinates are assigned
    merged_df["x_uwb"] = merged_df["x_shifted"]
    merged_df["y_uwb"] = merged_df["y_shifted"]

    # Error between pose and UWB is calculated
    merged_df["error_xy"] = np.sqrt(
        (merged_df[x_col_post] - merged_df["x_uwb"])**2 +
        (merged_df[y_col_post] - merged_df["y_uwb"])**2
    )

    # Selected columns are written to CSV
    output_cols = [
        "timestamp_norm (s)",
        "x_uwb", "y_uwb",
        x_col_post, y_col_post,
        "error_xy",
        "voxel_value"
    ]
    merged_df[output_cols].to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    POSE_FILE_LOOKUP = yaml_config["pose_file_lookup"]
    POSE_SUFFIX_LOOKUP = yaml_config["pose_suffix_lookup"]

    parser = argparse.ArgumentParser(description="Selecting the keyword for input file names check, "
                                     "selection and file check between amcl and odom")
    parser.add_argument("--keyword", type=str, default=yaml_config["keyword_stage6"],
                        help="Input should be '_converted' unless explicitly being tested")
    parser.add_argument("--uwb-csv", type=str, default=yaml_config["uwb_csv"],
                        help="Input should be '3_uwb_pose_shifted.csv' unless explicitly being tested")
    args = parser.parse_args()

    # Search for voxel JSON files and process them by type
    cwd = os.getcwd()
    voxel_jsons = [f for f in os.listdir(cwd) if f.endswith(".json") and args.keyword in f]

    if not voxel_jsons:
        print(f"No *_converted.json files found in: {cwd}")
        return

    for fname in voxel_jsons:
        f_lower = fname.lower()
        if "amcl" in f_lower:
            compute_error_and_save(fname, "amcl", args.uwb_csv, POSE_FILE_LOOKUP, POSE_SUFFIX_LOOKUP)
        elif "odom" in f_lower or "odometry" in f_lower:
            compute_error_and_save(fname, "odom", args.uwb_csv, POSE_FILE_LOOKUP, POSE_SUFFIX_LOOKUP)
        else:
            print(f"Skipped unrecognized file: {fname}")


if __name__ == "__main__":
    main()