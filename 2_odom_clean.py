"""
Early bag recordings occasionally produced all-zero rows
due to a data collection bug during initial lab work.
This script removes those rows before further processing.
Not required for the published bag files.
Kept for completeness and reproducibility.
"""

import pandas as pd
import os

def filter_zero_xyz_rows(df):
    """
    Remove rows where x, y, and z are all zero.

    Args:
        df (pd.DataFrame): Input DataFrame with columns 'x', 'y', 'z'.

    Returns:
        pd.DataFrame: DataFrame with all-zero rows removed.
    """
    mask = (df['x'] == 0) & (df['y'] == 0) & (df['z'] == 0)
    return df[~mask]


def remove_zero_xyz_rows():
    """
    Read odometry CSV, remove all-zero rows, and write cleaned output.
    """
    INPUT_CSV = "1_odometry_filtered.csv"
    OUTPUT_CSV = "2_odometry_filtered_clean.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, INPUT_CSV)
    output_csv = os.path.join(script_dir, OUTPUT_CSV)

    if not os.path.exists(input_csv):
        print(f"Input file not found: {input_csv}")
        return

    df = pd.read_csv(input_csv)
    cleaned_df = filter_zero_xyz_rows(df)

    cleaned_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    remove_zero_xyz_rows()