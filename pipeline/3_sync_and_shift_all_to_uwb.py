import os
import pandas as pd

if not os.path.exists(INPUT_ODOM):
    print(f"Input file not found: {INPUT_ODOM}")
    return
if not os.path.exists(INPUT_UWB):
    print(f"Input file not found: {INPUT_UWB}")
    return

INPUT_ODOM = "2_odometry_filtered_clean.csv"
INPUT_UWB = "1_uwb_pose.csv"
OUTPUT_UWB = "3_uwb_pose_shifted.csv"
OUTPUT_ODOM = "3_odometry_filtered_uwbSync.csv"
SYNC_TOLERANCE_S  = 0.5

def main():
    # Input files are loaded
    odom = pd.read_csv(INPUT_ODOM)
    uwb = pd.read_csv(INPUT_UWB)

    # UWB coordinates are shifted so the first point becomes the origin
    uwb = uwb.drop(index=0).reset_index(drop=True)
    x0, y0 = uwb.loc[0, 'x'], uwb.loc[0, 'y']
    uwb['x_shifted'] = uwb['x'] - x0
    uwb['y_shifted'] = uwb['y'] - y0
    uwb.to_csv(OUTPUT_UWB, index=False)

    # Odometry is synchronized to UWB timestamps with nearest-neighbor matching
    aligned_odom = pd.merge_asof(
        uwb[["timestamp_norm (s)"]],
        odom,
        on="timestamp_norm (s)",
        direction="nearest",
        tolerance=SYNC_TOLERANCE_S
    )
    aligned_odom = aligned_odom.dropna(subset=["x", "y", "z"])
    aligned_odom.to_csv(OUTPUT_ODOM, index=False)

if __name__ == "__main__":
    main()