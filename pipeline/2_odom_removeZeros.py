# Utility script:
# Early bag recordings occasionally produced all-zero rows
# due to a data collection bug during initial lab work.
# This script removes those rows before further processing.
# Not required for the published bag files.
# Kept for completeness and reproducibility.

import pandas as pd
import os
INPUT_CSV = "1_odometry_filtered.csv"
OUTPUT_CSV = "2_odometry_filtered_clean.csv"

def remove_zero_xyz_rows():
    # Current script directory is identified
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, INPUT_CSV)
    output_csv = os.path.join(script_dir, OUTPUT_CSV)

    if not os.path.exists(input_csv):
        print(f"Input file not found: {input_csv}")
        return

    df = pd.read_csv(input_csv)

    # Rows where x, y, z are all zero are excluded
    mask = (df['x'] == 0) & (df['y'] == 0) & (df['z'] == 0)
    cleaned_df = df[~mask]

    # Cleaned data is written to a new CSV file
    cleaned_df.to_csv(output_csv, index=False)
    print(f"Saved cleaned file to: {output_csv}")
    print(f"Removed {mask.sum()} rows with all-zero x, y, z.")
    print(f"{len(cleaned_df)} rows remaining.")

if __name__ == "__main__":
    remove_zero_xyz_rows()