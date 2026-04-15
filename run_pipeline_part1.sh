#!/bin/bash

#run_pipeline_part1.sh

set -e
python3 2_odom_clean.py
python3 3_sync_shift_to_uwb.py
python3 4_traject_resample.py
