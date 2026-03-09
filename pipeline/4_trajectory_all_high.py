import pandas as pd
import json
import numpy as np

# Offset values applied to coordinates (High offset version)
#OFFSET = {"x": 10.25, "y": 1.8, "z": -10} #lab offset
OFFSET = {"x": 47.5, "y": 1.8, "z": -2.2}

def extract_meterwise_trajectory(csv_path, output_path, meter_step):
    # Input CSV is read and rows without coordinates are dropped
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['x', 'y', 'z'])

    # Raw trajectory is created by applying offset and axis remapping
    trajectory_raw = [
        {
            "x": float(row['x']) + OFFSET["x"],
            "y": float(row['z']) + OFFSET["y"],
            "z": -float(row['y']) + OFFSET["z"]
        }
        for _, row in df.iterrows()
    ]

    # Distance between two points is calculated
    def distance(p1, p2):
        return np.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2 + (p1['z'] - p2['z'])**2)

    # A point is interpolated along a segment at a given ratio
    def interpolate(p1, p2, ratio):
        return {
            "x": p1["x"] + ratio * (p2["x"] - p1["x"]),
            "y": p1["y"] + ratio * (p2["y"] - p1["y"]),
            "z": p1["z"] + ratio * (p2["z"] - p1["z"]),
        }

    # First point is stored, then additional points are added every meter_step
    output_points = [trajectory_raw[0]]
    cumulative_dist = 0.0
    next_target = meter_step

    for i in range(1, len(trajectory_raw)):
        p_prev = trajectory_raw[i - 1]
        p_curr = trajectory_raw[i]
        segment_dist = distance(p_prev, p_curr)
        cumulative_dist += segment_dist

        # Interpolated point is inserted whenever cumulative distance reaches the step
        while cumulative_dist >= next_target:
            overshoot = cumulative_dist - next_target
            ratio = (segment_dist - overshoot) / segment_dist
            interp_point = interpolate(p_prev, p_curr, ratio)
            output_points.append(interp_point)
            next_target += meter_step

    # Final trajectory is written to JSON
    with open(output_path, "w") as f:
        json.dump({"trajectory": output_points}, f, indent=4)
    print(f"Saved {meter_step}m trajectory with {len(output_points)} points to: {output_path}")

# Odometry trajectory is generated at different step sizes
csv_path_odom = "3_odometry_filtered_uwbSync.csv"
extract_meterwise_trajectory(csv_path_odom, "4_trajectory_odom_high_1m.json", meter_step=1.0)
extract_meterwise_trajectory(csv_path_odom, "4_trajectory_odom_high_05m.json", meter_step=0.5)
extract_meterwise_trajectory(csv_path_odom, "4_trajectory_odom_high_02m.json", meter_step=0.2)
extract_meterwise_trajectory(csv_path_odom, "4_trajectory_odom_high_01m.json", meter_step=0.1)

