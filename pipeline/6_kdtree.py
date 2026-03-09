import os
import pandas as pd
import numpy as np
import json
from scipy.spatial import KDTree

# Configuration for file matching and input sources
KEYWORD = "_converted"
UWB_CSV = "3_uwb_pose_shifted.csv"
POSE_FILE_LOOKUP = {
    "amcl": "3_amcl_pose_uwbSync.csv",
    "odom": "3_odometry_filtered_uwbSync.csv"
}
POSE_SUFFIX_LOOKUP = {
    "amcl": "_amcl",
    "odom": "_odom"
}

def compute_error_and_save(voxel_json_path, pose_key):
    # Output filename is created with step prefix and suffix
    pose_suffix = POSE_SUFFIX_LOOKUP[pose_key]
    pose_csv = POSE_FILE_LOOKUP[pose_key]

    basename = os.path.splitext(voxel_json_path)[0]
    if basename.startswith("5_"):
        new_base = "6_" + basename[2:]
    else:
        new_base = basename
    output_csv = new_base + "_error.csv"

    print(f"\nProcessing: {voxel_json_path} → {output_csv}")

    # Input files are loaded
    uwb_df = pd.read_csv(UWB_CSV)
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

# Search for voxel JSON files and process them by type
cwd = os.getcwd()
voxel_jsons = [f for f in os.listdir(cwd) if f.endswith(".json") and KEYWORD in f]

if not voxel_jsons:
    print(f"No *_converted.json files found in: {cwd}")
else:
    for fname in voxel_jsons:
        f_lower = fname.lower()
        if "amcl" in f_lower:
            compute_error_and_save(fname, pose_key="amcl")
        elif "odom" in f_lower or "odometry" in f_lower:
            compute_error_and_save(fname, pose_key="odom")
        else:
            print(f"Skipped unrecognized file: {fname}")

