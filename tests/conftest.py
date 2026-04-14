# conftest.py
# Note: 1_extract_topics.py is excluded from this test suite.
# It requires a ROS 2 environment (rclpy, rosbag2_py) which is
# not available in standard CI. Manual testing only.

import pytest
import pandas as pd

@pytest.fixture
def sample_odom_df():
    return pd.DataFrame({
        "timestamp": [1.0, 2.0, 3.0, 4.0, 5.0],
        "x": [0.0, 1.0, 2.0, 3.0, 4.0],
        "y": [0.0, 0.5, 1.0, 1.5, 2.0],
        "z": [0.0, 0.0, 0.0, 0.0, 0.0],
    })

@pytest.fixture
def sample_uwb_df():
    return pd.DataFrame({
        "timestamp": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5],
        "x_uwb": [0.0, 1.87, 3.64, 3.73, 4.15, 2.14, 5.0, 3.78, 1.46, 2.57],
        "y_uwb": [0.0, 4.14, 4.99, 1.35, 2.53, 2.83, 1.84, 3.57, 4.57, 2.41],
    })

@pytest.fixture
def sample_stage2():
    return pd.DataFrame({
        "timestamp_abs (s)": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5],
        "timestamp_norm (s)": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5],
        "x": [0.00, 1.87, 0.00, 3.73, 0.00, 0.00, 5.01, 3.78, 0.00, 2.57],
        "y": [0.00, 4.14, 0.00, 0.00, 2.53, 2.83, 1.84, 0.00, 0.00, 2.41],
        "z": [0.00, 0.00, 1.52, 4.46, 0.00, 0.01, 0.00, 0.00, 0.00, 4.73],
        "qx":[0.00, 1.87, 0.00, 3.73, 0.00, 0.00, 5.01, 3.78, 0.00, 2.57], 
        "qy":[0.00, 4.14, 0.00, 0.00, 2.53, 2.83, 1.84, 0.00, 0.00, 2.41], 
        "qz":[0.00, 0.00, 1.52, 4.46, 0.00, 0.01, 0.00, 0.00, 0.00, 4.73], 
        "qw":[0.00, 4.14, 0.00, 0.00, 2.53, 2.83, 1.84, 0.00, 0.00, 2.41],
    })
