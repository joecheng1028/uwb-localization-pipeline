"""
Fits linear, quadratic, and exponential regression models to voxel reliability vs positioning error and saves plots.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import argparse
import yaml
import logging

logger = logging.getLogger(__name__)

# Exponential model used for curve fitting
def exp_model(
        x: np.ndarray, 
        a: float, 
        b: float, 
        c: float
        ) -> np.ndarray:
    """
    Exponential model passed to scipy curve_fit: a * (1 - exp(-b * x)) + c.

    Parameters
    ----------
    x : np.ndarray
        Input values.
    a, b, c : float
        Fitted coefficients optimised by curve_fit.

    Returns
    -------
    np.ndarray
        Model output at each point in x.
    """
    return a * (1 - np.exp(-b * x)) + c

# Sturges' formula for number of bins
def sturges_bins(n: int) -> int:
    """
    Calculating binning size/width under Sturges' rule

    Parameters
    ----------
    n : int
        Number of data points.

    Returns
    -------
    int
        Integer of the binning size
    """
    return int(np.ceil(np.log2(max(n, 1)) + 1))

# Plot voxel values with regression models and bin means
def plot_regressions(
        df: pd.DataFrame, 
        base_name: str
        ) -> None:
    """
    Plots the bin graph, curve fit for linear, quadratic and exponential regression models, and calculate R²

    Parameters
    ----------
    df : pd.DataFrame
        all .csv under same directory that matches with keyword
    base_name : str
        name of output files (plots)

    Returns
    -------
    None

    """
    x = df['error_xy'].values
    y = df['voxel_value'].values
    x_sorted = np.linspace(x.min(), x.max(), 300)

    # Linear regression
    coeffs_lin = np.polyfit(x, y, deg=1)
    y_lin = np.polyval(coeffs_lin, x_sorted)
    r2_lin = r2_score(y, np.polyval(coeffs_lin, x))

    # Quadratic regression
    coeffs_quad = np.polyfit(x, y, deg=2)
    y_quad = np.polyval(coeffs_quad, x_sorted)
    r2_quad = r2_score(y, np.polyval(coeffs_quad, x))

    # Exponential regression
    try:
        popt, _ = curve_fit(exp_model, x, y, p0=(10, 1, 22), maxfev=10000)
        y_exp = exp_model(x_sorted, *popt)
        r2_exp = r2_score(y, exp_model(x, *popt))

    except RuntimeError:
        logger.warning("Exponential fit failed for %s",base_name)
        y_exp = None
        r2_exp = None

    # Bin means are calculated with Sturges' rule
    k = sturges_bins(len(x))
    df['error_bin'] = pd.cut(df['error_xy'], bins=k)
    grouped = df.groupby('error_bin', observed=False)['voxel_value'].mean().reset_index()
    bin_centers = [interval.mid for interval in grouped['error_bin']]

    # Plot includes raw data, bin means, and regression fits
    plt.figure(figsize=(12, 6))
    plt.scatter(x, y, alpha=0.3, s=10, label="Raw data")
    plt.plot(bin_centers, grouped['voxel_value'], marker='o', color='black',
             label=f"Mean voxel per Sturges bin (k={k})")

    plt.plot(x_sorted, y_lin, 'r-', label=f"Linear fit (R² = {r2_lin:.3f})")
    plt.plot(x_sorted, y_quad, 'g--', label=f"Quadratic fit (R² = {r2_quad:.3f})")

    if y_exp is not None:
        plt.plot(x_sorted, y_exp, 'b:', label=f"Exponential fit (R² = {r2_exp:.3f})")

    plt.xlabel("2D Error (meters)")
    plt.ylabel("Voxel Value (Color Intensity)")
    plt.title(f"Voxel Value vs Error — All Regressions (Sturges bins)\n{base_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Plot is saved to file
    out_file = f"7_{base_name}_regressions.png"
    plt.savefig(out_file)
    logger.info("Saved: %s", out_file)
    plt.close()

# Main loop for scanning and plotting matching files
# Configuration for file matching
def main() -> None:
    CSV_SUFFIX = ".csv"

    # yaml
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    # Parser

    parser = argparse.ArgumentParser(description="Keyword of Input file")
    parser.add_argument("--keyword", type=str, default=yaml_config["keyword_stage7"],
                        help="'keyword_stage7' unless under testing")
    args = parser.parse_args()

    cwd = os.getcwd()
    csv_files = [f for f in os.listdir(cwd) if f.endswith(CSV_SUFFIX) and args.keyword in f]

    if not csv_files:
        raise FileNotFoundError(f"csv file not found: {args.keyword}")
    else:
        for file in csv_files:
            df = pd.read_csv(file)
            base_name = os.path.splitext(file)[0].replace("6_", "7_")
            plot_regressions(df, base_name)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    main()
