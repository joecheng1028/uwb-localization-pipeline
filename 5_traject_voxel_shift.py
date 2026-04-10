"""
This module remap the axis due to the simulation output disrupting the alignment between robot odometry and UWB data.
"""
import os
import json
import yaml
import argparse


# Configuration for keyword matching and output naming
# KEYWORD = "_voxels"
# OUTPUT_SUFFIX = "_converted.json"

# yaml
script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(script_dir, "config.yaml")

# Connecting script with external config
with open(yaml_path, "r") as f:
    yaml_config = yaml.safe_load(f)

# 1 argparse for all:
parser = argparse.ArgumentParser(description="Selecting keyword for the input file to be looked for and suffix for output file.")
parser.add_argument("--keyword", type=str, default = yaml_config["keyword_stage5"], 
                    help="Input should contain '_voxels' unless explicitly being tested")
parser.add_argument("--output-suffix", type=str, default = yaml_config["output_suffix_stage5"], 
                    help="Input should contain 'output_suffix_stage5' unless explicitly being tested")
args = parser.parse_args()
KEYWORD = args.keyword
OUTPUT_SUFFIX = args.output_suffix

def swap_and_normalize(coord, dx, dy, dz):
    """
    This part remaps the framing to match with the pipeline and shift the origin to 0, 0, 0 as starting point
    Args:
        coord (dict): Input coordinate with keys 'x', 'y', 'z'.
        dx (float): X offset of the reference origin point.
        dy (float): Y offset of the reference origin point.
        dz (float): Z offset of the reference origin point.

    Returns:
        dict: Remapped and shifted coordinate with keys 'x', 'y', 'z'.
    """
    # Coordinates are shifted to origin and axes are remapped
    x_new = coord["x"] - dx
    y_new = -(coord["z"] - dz)
    z_new = coord["y"] - dy
    return {"x": x_new, "y": y_new, "z": z_new}

# All JSON files containing the keyword are listed, AMCL files excluded
script_dir = os.path.dirname(os.path.abspath(__file__))
json_files = [
    f for f in os.listdir(script_dir)
    if f.endswith(".json") and KEYWORD in f and "amcl" not in f.lower()
]

if not json_files:
    print(f"No JSON files found with keyword '{KEYWORD}' (excluding AMCL) in: {script_dir}")
    exit()

# Each matching file is processed
for fname in json_files:
    fpath = os.path.join(script_dir, fname)
    with open(fpath, 'r') as f:
        data = json.load(f)

    # First trajectory point is used as reference origin
    origin = data[0]["trajPoint"]
    x0, y0, z0 = origin["x"], origin["y"], origin["z"]

    # All entries are normalized and stored in new format
    converted_data = []
    for entry in data:
        converted_entry = {
            "index": entry["index"],
            "trajPoint": swap_and_normalize(entry["trajPoint"], x0, y0, z0),
            "voxel": {
                "min": swap_and_normalize(entry["voxel"]["min"], x0, y0, z0),
                "max": swap_and_normalize(entry["voxel"]["max"], x0, y0, z0),
                "value": entry["voxel"]["value"]
            }
        }
        converted_data.append(converted_entry)

    # Output filename is built with consistent prefix and suffix
    if fname.startswith("4_"):
        stripped_name = fname[2:]
        output_fname = "5_" + os.path.splitext(stripped_name)[0] + OUTPUT_SUFFIX
    else:
        output_fname = os.path.splitext(fname)[0] + OUTPUT_SUFFIX

    # Converted data is written to JSON
    output_path = os.path.join(script_dir, output_fname)
    with open(output_path, "w") as f:
        json.dump(converted_data, f, indent=2)

    print(f"✔ Converted: {fname} → {output_fname}")