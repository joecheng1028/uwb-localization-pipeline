"""
This module calculates different statistics of positioning error without considering reliability index
"""
import pandas as pd
import numpy as np
import os
import glob
import argparse
import yaml
import logging

logger = logging.getLogger(__name__)

def compute_metrics_from_columns(
        df: pd.DataFrame, 
        x_true_col: str, 
        y_true_col: str, 
        x_est_col: str, 
        y_est_col: str
        ) -> dict:
    """
    Calculate statistics reflecting accuracy of UWB to robot odometry

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe from .csv with keyword
    x_true_col : str
        x-odometry (robot position)
    y_true_col : str
        y-odometry
    x_est_col : str
        x-uwb data (UWB tag)
    y_est_col : str
        y-uwb data

    Returns
    -------
    dict
        quantity of dataframe
        sigma of error in x- and y-coordinate
        mean of x- and y-coordinate error
        positioning error: minimum, maximum, mean, median and standard deviation
        RMSE: Root mean square error
        DRMS: Distance Root Mean Squared
        2DRMS: 2 * DRMS
        CEP50: Radius of the circle covering 50% of positioning error
        R95: Radius of the circle covering 95% of positioning error
        2D Precision
    """
    dx = df[x_est_col] - df[x_true_col]
    dy = df[y_est_col] - df[y_true_col]
    error_2d = np.sqrt(dx**2 + dy**2)
    df['error_2d'] = error_2d

    sigma_x = np.std(dx)
    sigma_y = np.std(dy)
    error_std = np.std(error_2d)

    mean_abs_dx = np.mean(np.abs(dx))
    mean_abs_dy = np.mean(np.abs(dy))
    error_min = np.min(error_2d)
    error_max = np.max(error_2d)
    error_mean = np.mean(error_2d)
    error_median = np.median(error_2d)

    rmse = np.sqrt(np.mean(error_2d ** 2))
    drms = np.sqrt(sigma_x ** 2 + sigma_y ** 2)
    drms_2 = 2 * drms
    cep50 = np.percentile(error_2d, 50)
    r95 = np.percentile(error_2d, 95)
    sigma_2d = np.sqrt(np.mean(dx ** 2 + dy ** 2))

    return {
        'count': len(df),
        'σ_x': sigma_x,
        'σ_y': sigma_y,
        'mean_abs_dx': mean_abs_dx,
        'mean_abs_dy': mean_abs_dy,
        'error_min': error_min,
        'error_max': error_max,
        'error_mean': error_mean,
        'error_median': error_median,
        'error_std': error_std,
        'RMSE': rmse,
        'DRMS': drms,
        '2DRMS': drms_2,
        'CEP50': cep50,
        'R95': r95,
        '2D Precision (σ₂D)': sigma_2d
    }

def process_file(file_path: str) -> None:
    """
    Fetch the input data with "pattern" and call function for calculating stats

    Parameters
    ----------
    file_path : str
        All files at directory that match with "pattern"

    Returns
    -------
    None

    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found {file_path}")
    
    df = pd.read_csv(file_path)

    metrics = compute_metrics_from_columns(df, 'x_odom', 'y_odom', 'x_uwb', 'y_uwb')

    original_name = os.path.basename(file_path)
    stripped_name = original_name.replace("6_", "8_", 1)
    base_name = os.path.splitext(stripped_name)[0]
    output_path = os.path.join(os.path.dirname(file_path), base_name + "_stat.txt")

    with open(output_path, "w") as f:
        f.write(f"2D Position Accuracy Metrics for {original_name}\n")
        f.write("===============================================\n\n")

        f.write("[Summary Info]\n")
        f.write(f"Sample count: {metrics['count']}\n\n")

        f.write("[Basic Error Stats]\n")
        f.write(f"Min error: {metrics['error_min']:.4f} m\n")
        f.write(f"Max error: {metrics['error_max']:.4f} m\n")
        f.write(f"Mean error: {metrics['error_mean']:.4f} m\n")
        f.write(f"Median error: {metrics['error_median']:.4f} m\n")
        f.write(f"Std dev of error: {metrics['error_std']:.4f} m\n\n")

        f.write("[Interim Results]\n")
        f.write(f"σ_x (std dev of dx): {metrics['σ_x']:.4f} m\n")
        f.write(f"σ_y (std dev of dy): {metrics['σ_y']:.4f} m\n")
        f.write(f"Mean absolute dx: {metrics['mean_abs_dx']:.4f} m\n")
        f.write(f"Mean absolute dy: {metrics['mean_abs_dy']:.4f} m\n\n")

        f.write("[Final Accuracy Metrics]\n")
        f.write(f"RMSE: {metrics['RMSE']:.4f} m\n")
        f.write(f"DRMS: {metrics['DRMS']:.4f} m\n")
        f.write(f"2DRMS: {metrics['2DRMS']:.4f} m\n")
        f.write(f"CEP50: {metrics['CEP50']:.4f} m\n")
        f.write(f"R95: {metrics['R95']:.4f} m\n")
        f.write(f"2D Precision (σ₂D): {metrics['2D Precision (σ₂D)']:.4f} m\n")

    logger.info("Written: %s", output_path)

# Main loop for scanning and processing files
def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description="Keyword for input file to match with")
    parser.add_argument("--pattern", type=str, default=yaml_config["pattern"],
                        help="'pattern' unless testing")
    args = parser.parse_args()

    files = glob.glob(args.pattern)

    if not files:
        raise FileNotFoundError("No matching files found.")

    for file_path in files:
        process_file(file_path)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    main()
