
import rclpy
import rosbag2_py
import csv
import os
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import yaml

def write_csv_header(writer):
    """
    Write the header of the output .csv
    """
    writer.writerow([
        'timestamp_abs (s)', 'timestamp_norm (s)', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'
    ])

def main():
    """
    This module imports positioning data of a real life robot installed with UWB tag
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "config.yaml")

    with open(yaml_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    TOPICS = yaml_config["topic"]

    # === Topic configuration for extraction ===
    # TOPICS = {
    #     '/odometry/filtered': {
    #         'msg_type': 'nav_msgs/msg/Odometry',
    #         'csv': '1_odometry_filtered.csv',
    #         'scale10': False
    #     },
    #     '/uwb_pose': {
    #         'msg_type': 'geometry_msgs/msg/PoseWithCovarianceStamped',
    #         'csv': '1_uwb_pose.csv',
    #         'scale10': True
    #     }
    # }

    """
    This looks for .db3 at the same directory, extract and export the data from ROS2 specific topics into a .csv file
    """
    bag_folder = os.path.abspath(os.path.dirname(__file__))
    db3_files = sorted([f for f in os.listdir(bag_folder) if f.endswith('.db3')])
    if not db3_files:
        print("No .db3 file found in this folder!")
        return

    bag_file = db3_files[0]
    bag_path = os.path.join(bag_folder, bag_file)
    print(f"Using bag: {bag_file}")
    
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
        print("Selected topics extracted:")
        for topic, cfg in TOPICS.items():
            print(f"   • {topic} -> {cfg['csv']}")
    finally:
        rclpy.shutdown()
        
if __name__ == "__main__":
    main()
