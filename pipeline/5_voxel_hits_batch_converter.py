import os
import json

# Configuration for keyword matching and output naming
KEYWORD = "_voxels"
OUTPUT_SUFFIX = "_converted.json"

def swap_and_normalize(coord, dx, dy, dz):
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

