import os
import pandas as pd

def shift_uwb_origin(uwb_df):
    """
    Drop the first row and shift UWB coordinates so the first point becomes the origin.

    Args:
        uwb_df (pd.DataFrame): Raw UWB DataFrame with columns 'x', 'y'.

    Returns:
        pd.DataFrame: UWB DataFrame with 'x_shifted' and 'y_shifted' columns added.
    """
    uwb = uwb_df.drop(index=0).reset_index(drop=True)
    x0, y0 = uwb.loc[0, 'x'], uwb.loc[0, 'y']
    uwb['x_shifted'] = uwb['x'] - x0
    uwb['y_shifted'] = uwb['y'] - y0
    return uwb


def sync_odom_to_uwb(uwb_df, odom_df, tolerance):
    """
    Synchronize odometry to UWB timestamps using nearest-neighbor matching.

    Args:
        uwb_df (pd.DataFrame):  UWB DataFrame with 'timestamp_norm (s)' column.
        odom_df (pd.DataFrame): Odometry DataFrame with 'timestamp_norm (s)' column.
        tolerance (float):      Maximum allowed time difference in seconds.

    Returns:
        pd.DataFrame: Odometry rows aligned to UWB timestamps, NaN rows dropped.
    """
    aligned = pd.merge_asof(
        uwb_df[["timestamp_norm (s)"]],
        odom_df,
        on="timestamp_norm (s)",
        direction="nearest",
        tolerance=tolerance
    )
    return aligned.dropna(subset=["x", "y", "z"])


def main():
    INPUT_ODOM = "2_odometry_filtered_clean.csv"
    INPUT_UWB = "1_uwb_pose.csv"
    OUTPUT_UWB = "3_uwb_pose_shifted.csv"
    OUTPUT_ODOM = "3_odometry_filtered_uwbSync.csv"
    SYNC_TOLERANCE_S = 0.5

    if not os.path.exists(INPUT_ODOM):
        print(f"Input file not found: {INPUT_ODOM}")
        return
    if not os.path.exists(INPUT_UWB):
        print(f"Input file not found: {INPUT_UWB}")
        return

    odom = pd.read_csv(INPUT_ODOM)
    uwb = pd.read_csv(INPUT_UWB)

    uwb = shift_uwb_origin(uwb)
    uwb.to_csv(OUTPUT_UWB, index=False)

    aligned_odom = sync_odom_to_uwb(uwb, odom, SYNC_TOLERANCE_S)
    aligned_odom.to_csv(OUTPUT_ODOM, index=False)


if __name__ == "__main__":
    main()