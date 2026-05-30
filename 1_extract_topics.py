import rclpy
import rosbag2_py
import csv
import os
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import yaml
import argparse
import logging

logger = logging.getLogger(__name__)

def write_csv_header(writer) -> None:
    """
    Write the header of the output .csv

    Parameters
    ----------
    writer : any
        csv.writer object for the output file. Black box not worthy of time

    Returns
    -------
    None

    """
    writer.writerow([
        'timestamp_abs (s)', 'timestamp_norm (s)', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'
    ])

def main() -> None:
    """
    This module imports positioning data of a real life robot installed with UWB tag
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    TOPICS = yaml_config["topic"]

    bag_folder = os.path.abspath(os.path.dirname(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", type=str, default=None,
                        help="Path to .db3 file. If omitted, auto-detects when exactly one exists.")
    args = parser.parse_args()

    if args.bag:
        bag_path = args.bag
        if not os.path.exists(bag_path):
            raise FileNotFoundError(f"Bag file not found: {bag_path}")
    else:
        db3_files = sorted(f for f in os.listdir(bag_folder) if f.endswith('.db3'))
        if not db3_files:
            raise FileNotFoundError(f"No .db3 file found in {bag_folder}")
        if len(db3_files) > 1:
            raise RuntimeError(
                f"Multiple .db3 files found in {bag_folder}: {db3_files}. "
                f"Pass --bag explicitly."
            )
        bag_path = os.path.join(bag_folder, db3_files[0])

    logger.info("Using bag: %s", bag_path)

    rclpy.init()
    try:
        storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='sqlite3')
        converter_options = rosbag2_py.ConverterOptions('', '')
        reader = rosbag2_py.SequentialReader()
        reader.open(storage_options, converter_options)

        selected_topics = list(TOPICS.keys())
        reader.set_filter(rosbag2_py.StorageFilter(topics=selected_topics))

        writers = {}
        files = {}
        types = {}
        for topic, config in TOPICS.items():
            files[topic] = open(config['csv'], 'w', newline='')
            writers[topic] = csv.writer(files[topic])
            write_csv_header(writers[topic])
            types[topic] = get_message(config['msg_type'])
        try:
            first_timestamp = None
            while reader.has_next():
                topic, data, t = reader.read_next()
                if topic not in TOPICS:
                    continue

                # Shift starting time to zero.
                if first_timestamp is None:
                    first_timestamp = t
                timestamp_abs = t * 1e-9
                timestamp_norm = (t - first_timestamp) * 1e-9

                # Decode the ROS message and select the topic config.
                msg = deserialize_message(data, types[topic])
                pose = msg.pose.pose
                cfg = TOPICS[topic]

                # Frame remap/alignment
                if topic == '/uwb_pose':
                    x_out = pose.position.x
                    y_out = pose.position.y
                elif topic == '/odometry/filtered':
                    x_out = -pose.position.x
                    y_out = -pose.position.y
                else:
                    x_out = pose.position.x
                    y_out = pose.position.y

                # Scaling if needed for topic
                z_out = pose.position.z
                if cfg['scale10']:
                    x_out /= 10
                    y_out /= 10
                    z_out /= 10

                # Write position and orientation
                writers[topic].writerow([
                    timestamp_abs,
                    timestamp_norm,
                    x_out, y_out, z_out,
                    pose.orientation.x,
                    pose.orientation.y,
                    pose.orientation.z,
                    pose.orientation.w
                ])
        finally:
            # Close all CSV files.
            for f in files.values():
                f.close()

        # Report output locations per topic.
        logger.info("Selected topics extracted:")
        for topic, cfg in TOPICS.items():
            logger.info("   • %s -> %s", topic, cfg['csv'])
    finally:
        rclpy.shutdown()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    main()
