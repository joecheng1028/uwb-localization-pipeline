import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuration for file matching
KEYWORD = "_voxels_converted_error"
CSV_SUFFIX = ".csv"
OUTPUT_PLOT = "7c_plot_sturges.png"

# Sturges’ formula for number of bins
def sturges_bins(n):
    return int(np.ceil(np.log2(n) + 1))

# Plot voxel values using Sturges’ binning rule
def plot_sturges(df, base_name):
    x = df['error_xy'].values
    y = df['voxel_value'].values

    # Number of bins is computed by Sturges’ rule
    k = sturges_bins(len(x))
    df['error_bin'] = pd.cut(df['error_xy'], bins=k)
    grouped = df.groupby('error_bin', observed=False)['voxel_value'].mean().reset_index()
    bin_centers = [interval.mid for interval in grouped['error_bin']]

    # Plot is created with raw scatter and mean per bin
    plt.figure(figsize=(12, 6))
    plt.scatter(x, y, alpha=0.25, s=10, label='Raw data')
    plt.plot(bin_centers, grouped['voxel_value'], 'ko-', label=f'Sturges Mean (k={k})')

    plt.xlabel("2D Error (meters)")
    plt.ylabel("Voxel Value (Color Intensity)")
    plt.title(f"Voxel Value vs Error — Sturges Binning\n{base_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Plot is saved to file
    plt.savefig(OUTPUT_PLOT)
    print(f"Saved: {OUTPUT_PLOT}")
    plt.close()

def main():
    # Main loop for scanning and plotting matching files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = [f for f in os.listdir(script_dir) if f.endswith(CSV_SUFFIX) and KEYWORD in f]

    if not csv_files:
        print(f"No matching *{KEYWORD}*.csv files found.")
        return
    for file in csv_files:
        df = pd.read_csv(file)
        base_name = os.path.splitext(file)[0].replace("6_", "7_")
        plot_sturges(df, base_name)

if __name__ == "__main__":
    main()