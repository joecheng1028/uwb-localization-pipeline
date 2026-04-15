#!/bin/bash

#run_pipeline_part2.sh

set -e
python3 5_traject_voxel_shift.py
python3 6_error_kdtree.py
python3 7_plot_regressions.py
python3 8_position_accuracy.py
