"""Resamples odometry trajectory and exports to JSON at fixed, multiple distance intervals."""
import pandas as pd
import json
import numpy as np
import argparse
import yaml
import os

def distance(p1, p2):
    """Calculates the distances between each 3D positioning point (effectively 2D)"""
    return np.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2 + (p1['z'] - p2['z'])**2)

def interpolate(p1, p2, ratio):
    """Returns an interpolated 3D point at a given fractional position along the segment from p1 to p2."""
    return {
        "x": p1["x"] + ratio * (p2["x"] - p1["x"]),
        "y": p1["y"] + ratio * (p2["y"] - p1["y"]),
        "z": p1["z"] + ratio * (p2["z"] - p1["z"]),
    }

def extract_meterwise_trajectory(csv_path, output_path, meter_step, offset):
    """ Resamples odometry CSV into fixed-distance trajectory points and writes to .json:
    csv_path:       provide the targeted .csv to read
    output_path:    define names of the output .json files
    meter_step:     trajectory of different resolutions
    offset:         select the different height of UWB tag on robot

    Returns:        Nothing
    """
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['x', 'y', 'z'])

    trajectory_raw = [
        {
            "x": float(row['x']) + offset["x"],
            "y": float(row['z']) + offset["y"],
            "z": -float(row['y']) + offset["z"]
        }
        for _, row in df.iterrows()
    ]

    output_points = [trajectory_raw[0]]
    cumulative_dist = 0.0
    next_target = meter_step

    for i in range(1, len(trajectory_raw)):
        p_prev = trajectory_raw[i - 1]
        p_curr = trajectory_raw[i]
        segment_dist = distance(p_prev, p_curr)
        cumulative_dist += segment_dist

        while cumulative_dist >= next_target:
            overshoot = cumulative_dist - next_target
            ratio = (segment_dist - overshoot) / segment_dist
            interp_point = interpolate(p_prev, p_curr, ratio)
            output_points.append(interp_point)
            next_target += meter_step

    with open(output_path, "w") as f:
        json.dump({"trajectory": output_points}, f, indent=4)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description="Selecting offset from High or Low")
    parser.add_argument("--profile", type=str, default="high", choices=["high", "low"],
                        help="--high when tag was installed on 'high' setting or --low when on 'low' setting")
    args = parser.parse_args()

    offset = yaml_config[f"offset_{args.profile}"]
    csv_path_odom = "3_odometry_filtered_uwbSync.csv"

    extract_meterwise_trajectory(csv_path_odom, f"4_trajectory_odom_{args.profile}_1m.json",  meter_step=1.0, offset=offset)
    extract_meterwise_trajectory(csv_path_odom, f"4_trajectory_odom_{args.profile}_05m.json", meter_step=0.5, offset=offset)
    extract_meterwise_trajectory(csv_path_odom, f"4_trajectory_odom_{args.profile}_02m.json", meter_step=0.2, offset=offset)
    extract_meterwise_trajectory(csv_path_odom, f"4_trajectory_odom_{args.profile}_01m.json", meter_step=0.1, offset=offset)


if __name__ == "__main__":
    main()