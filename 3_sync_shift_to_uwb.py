import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def shift_uwb_origin(uwb_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop the first row and shift UWB coordinates so the first point becomes the origin.

    Parameters
    ----------
    uwb_df : pd.DataFrame
        Raw UWB DataFrame with columns 'x', 'y'.

    Returns
    -------
    pd.DataFrame
        UWB DataFrame with 'x_shifted' and 'y_shifted' columns added.
    """
    uwb = uwb_df.drop(index=0).reset_index(drop=True)
    x0, y0 = uwb.loc[0, 'x'], uwb.loc[0, 'y']
    uwb['x_shifted'] = uwb['x'] - x0
    uwb['y_shifted'] = uwb['y'] - y0
    logger.info("UWB data shifted row successful")
    return uwb


def sync_odom_to_uwb(
        uwb_df: pd.DataFrame,
        odom_df: pd.DataFrame,
        tolerance: float
        ) -> pd.DataFrame:
    """
    Synchronize odometry to UWB timestamps using nearest-neighbor matching.

    Parameters
    ----------
    uwb_df : pd.DataFrame
        UWB DataFrame with 'timestamp_norm (s)' column.

    odom_df : pd.DataFrame
        Odometry DataFrame with 'timestamp_norm (s)' column.

    tolerance : float
        Maximum allowed time difference in seconds.

    Returns
    -------
    pd.DataFrame
        Odometry rows aligned to UWB timestamps, NaN rows dropped.
    """
    aligned = pd.merge_asof(
        uwb_df[["timestamp_norm (s)"]],
        odom_df,
        on="timestamp_norm (s)",
        direction="nearest",
        tolerance=tolerance      # type: ignore[arg-type]  # numeric merge_asof; stubs omit float
    )
    logger.info("time synchronization between 2 data set completed.")
    return aligned.dropna(subset=["x", "y", "z"])


def main() -> None:
    INPUT_ODOM = "2_odometry_filtered_clean.csv"
    INPUT_UWB = "1_uwb_pose.csv"
    OUTPUT_UWB = "3_uwb_pose_shifted.csv"
    OUTPUT_ODOM = "3_odometry_filtered_uwbSync.csv"
    SYNC_TOLERANCE_S = 0.5

    if not os.path.exists(INPUT_ODOM):
        raise FileNotFoundError(f"Input file not found: {INPUT_ODOM}")
    if not os.path.exists(INPUT_UWB):
        raise FileNotFoundError(f"Input file not found: {INPUT_UWB}")

    odom = pd.read_csv(INPUT_ODOM)
    uwb = pd.read_csv(INPUT_UWB)

    uwb = shift_uwb_origin(uwb)
    uwb.to_csv(OUTPUT_UWB, index=False)

    aligned_odom = sync_odom_to_uwb(uwb, odom, SYNC_TOLERANCE_S)
    aligned_odom.to_csv(OUTPUT_ODOM, index=False)
    logger.info("Saved uwb data with shifted origin as %s", OUTPUT_UWB)
    logger.info("Saved synchronized odometry data as %s", OUTPUT_ODOM)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s"
    )
    main()
