"""
This module remap the axis due to the simulation output disrupting the alignment between robot odometry and UWB data.
"""
import os
import json
import yaml
import argparse
import logging

logger = logging.getLogger(__name__)

def axis_shift(
        coord: dict,
        dx: float, 
        dy: float, 
        dz: float
        ) -> dict:
    """
    Remaps the framing to match with the pipeline and shift the origin to 0, 0, 0 as starting point

    Parameters
    ----------
    coord : dict
        Input coordinate with keys 'x', 'y', 'z'.
    dx : float
        X offset of the reference origin point.
    dy : float
        Y offset of the reference origin point.
    dz : float
        Z offset of the reference origin point.

    Returns
    -------
    dict
        Remapped and shifted coordinate with keys 'x', 'y', 'z'.
    """
    x_new = coord["x"] - dx
    y_new = -(coord["z"] - dz)
    z_new = coord["y"] - dy
    return {"x": x_new, "y": y_new, "z": z_new}


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description="Selecting keyword for the input file to be looked for and suffix for output file.")
    parser.add_argument("--keyword", type=str, default=yaml_config["keyword_stage5"],
                        help="Input should contain '_voxels' unless explicitly being tested")
    parser.add_argument("--output-suffix", type=str, default=yaml_config["output_suffix_stage5"],
                        help="Input should contain 'output_suffix_stage5' unless explicitly being tested")
    args = parser.parse_args()

    keyword = args.keyword
    output_suffix = args.output_suffix

    # All JSON files containing the keyword are listed, AMCL files excluded
    json_files = [
        f for f in os.listdir(script_dir)
        if f.endswith(".json") and keyword in f and "amcl" not in f.lower()
    ]

    if not json_files:
        raise FileNotFoundError(f"No JSON files found with keyword '{keyword}' in: {script_dir}")
    
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
                "trajPoint": axis_shift(entry["trajPoint"], x0, y0, z0),
                "voxel": {
                    "min": axis_shift(entry["voxel"]["min"], x0, y0, z0),
                    "max": axis_shift(entry["voxel"]["max"], x0, y0, z0),
                    "value": entry["voxel"]["value"]
                }
            }
            converted_data.append(converted_entry)

        # Output filename is built with consistent prefix and suffix
        if fname.startswith("4_"):
            stripped_name = fname[2:]
            output_fname = "5_" + os.path.splitext(stripped_name)[0] + output_suffix
        else:
            output_fname = os.path.splitext(fname)[0] + output_suffix

        # Converted data is written to JSON
        output_path = os.path.join(script_dir, output_fname)

        with open(output_path, "w") as f:
            json.dump(converted_data, f, indent=2)

        logger.info("Saved processed file at %s", output_path)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    main()
