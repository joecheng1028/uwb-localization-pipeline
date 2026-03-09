# 7a_plot_k_Manual.py (manual bin width version)
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuration for file matching and bin settings
KEYWORD = "_voxels_converted_error"
CSV_SUFFIX = ".csv"
BIN_WIDTH = 0.1  # meters
MAX_RANGE_M = None  # optional cap for x-axis range
OUTPUT_PLOT = "7a_plot_k_Manual.png"


def _ceil_to_multiple(x: float, step: float) -> float:
    # Value is rounded up to the next multiple of step
    if x <= 0:
        return 0.0
    k = math.ceil((x - 1e-12) / step)
    return round(k * step, 10)

def _verify_columns(df: pd.DataFrame, file: str):
    # Required columns are checked before plotting
    required = {"error_xy", "voxel_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{file}: missing required columns: {sorted(missing)}")

def plot_voxel_vs_error(df: pd.DataFrame, base_name: str, file: str):
    _verify_columns(df, file)

    # Error values are extracted
    err = df["error_xy"].to_numpy()
    if err.size == 0:
        print(f"{file}: no rows; skipping.")
        return

    # Bin range is determined from data and adjusted if max range is set
    data_max = float(np.nanmax(err))
    upper = _ceil_to_multiple(data_max, BIN_WIDTH)
    if MAX_RANGE_M is not None:
        upper = min(upper, MAX_RANGE_M)

    if upper <= 0:
        upper = BIN_WIDTH

    # Bin edges are created with epsilon for inclusion of last edge
    eps = 1e-12
    bin_edges = np.arange(0.0, upper + BIN_WIDTH + eps, BIN_WIDTH)

    # Errors are assigned into bins
    df = df.copy()
    df["error_bin"] = pd.cut(df["error_xy"], bins=bin_edges, include_lowest=True)

    # Mean voxel values per bin are calculated
    grouped = df.groupby("error_bin", observed=False)["voxel_value"] \
                .agg(["mean", "count"]).reset_index()

    # Bin centers are extracted for plotting
    bin_centers = [interval.mid for interval in grouped["error_bin"]]

    # Plot is created with scatter points and bin means
    plt.figure(figsize=(12, 6))
    plt.scatter(df["error_xy"], df["voxel_value"], alpha=0.3, s=10, label="Raw data")
    plt.plot(bin_centers, grouped["mean"], marker="o", linewidth=1.5,
             label=f"Mean per {BIN_WIDTH} m bin")

    plt.xlabel("2D Error (meters)")
    plt.ylabel("Voxel Value (Color Intensity)")
    plt.title(f"Voxel Value vs Error (manual bins @ {BIN_WIDTH} m)\n{base_name}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Plot is saved to file
    plt.savefig(OUTPUT_PLOT, dpi=200)
    print(f"Saved plot: {OUTPUT_PLOT}")
    plt.close()

# Main loop for scanning and plotting matching files
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = [f for f in os.listdir(script_dir) if f.endswith(CSV_SUFFIX) and KEYWORD in f]

    if not csv_files:
        print(f"No matching *{KEYWORD}*.csv files found in: {script_dir}")
        return

    for file in csv_files:
        df = pd.read_csv(file)
        base_name = os.path.splitext(file)[0].replace("6_", "7_")
        plot_voxel_vs_error(df, base_name, file)

if __name__ == "__main__":
    main()