import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuration for file matching
KEYWORD = "_voxels_converted_error"
CSV_SUFFIX = ".csv"
OUTPUT_PLOT = "7b_plot_conventionals.png"

# Binning strategies based on different statistical rules
def sturges_bins(n):
    return int(np.ceil(np.log2(n) + 1))

def sqrt_bins(n):
    return int(np.ceil(np.sqrt(n)))

def freedman_diaconis_bin_width(data):
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    n = len(data)
    return 2 * iqr * (n ** (-1/3))

def get_bin_configs(data):
    # Number of bins is computed for each method
    n = len(data)
    rng = data.max() - data.min()
    bin_fd = freedman_diaconis_bin_width(data)
    return {
        "sturges": int(np.ceil(rng / (rng / sturges_bins(n)))),
        "sqrt": int(np.ceil(rng / (rng / sqrt_bins(n)))),
        "freedman_diaconis": int(np.ceil(rng / bin_fd)) if bin_fd > 0 else 1
    }

# Plot mean voxel values using different binning strategies
def plot_voxel_comparison(df, base_name):
    bin_configs = get_bin_configs(df['error_xy'])
    plt.figure(figsize=(12, 6))

    for method, bins in bin_configs.items():
        df['error_bin'] = pd.cut(df['error_xy'], bins=bins)
        grouped = df.groupby('error_bin', observed=False)['voxel_value'].mean().reset_index()
        bin_centers = [interval.mid for interval in grouped['error_bin']]
        plt.plot(bin_centers, grouped['voxel_value'], marker='o', label=f"{method} ({bins} bins)")

    plt.xlabel("2D Error (meters)")
    plt.ylabel("Mean Voxel Value (Color Intensity)")
    plt.title(f"Voxel Value vs Error — Bin Strategy Comparison\n{base_name}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
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
        plot_voxel_comparison(df, base_name)
            
if __name__ == "__main__":
    main()