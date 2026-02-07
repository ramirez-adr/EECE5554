#!/usr/bin/env python3
import csv
import rosbag2_py

from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


BAG_PATH = "LAB1/src/data/straight_line2/straight_line2_0.mcap"
TOPIC = "/gps"
OUT_CSV = "straight_line_data_1_gps.csv"


def main():
    # Open MCAP bag
    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    # Map topic -> message type string
    topics_and_types = reader.get_all_topics_and_types()
    type_map = {tt.name: tt.type for tt in topics_and_types}

    if TOPIC not in type_map:
        raise RuntimeError(f"Topic {TOPIC} not found. Available: {list(type_map.keys())}")

    msg_type = get_message(type_map[TOPIC])  # e.g. gps_driver/msg/GpsMsg

    # We don't know your exact fields, so we write a "best effort":
    # timestamp + then any common GPS fields if they exist.
    def safe_get(obj, attr, default=""):
        return getattr(obj, attr, default)

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)

        # Header: include a few likely fields; blanks will be empty if not present.
        w.writerow([
            "bag_time_ns",
            "header_stamp_sec",
            "header_stamp_nanosec",
            "frame_id",
            "latitude",
            "longitude",
            "altitude",
            "utm_easting",
            "utm_northing",
            "zone",
            "letter",
            "hdop",
            "fix_quality",
            "num_satellites",
            "speed",
            "track",
        ])

        count = 0
        while reader.has_next():
            topic, data, t = reader.read_next()
            if topic != TOPIC:
                continue

            msg = deserialize_message(data, msg_type)

            # header fields (if your msg has header)
            header = safe_get(msg, "header", None)
            if header is not None:
                stamp = safe_get(header, "stamp", None)
                stamp_sec = safe_get(stamp, "sec", "")
                stamp_nsec = safe_get(stamp, "nanosec", "")
                frame_id = safe_get(header, "frame_id", "")
            else:
                stamp_sec = stamp_nsec = frame_id = ""

            w.writerow([
                t,
                stamp_sec,
                stamp_nsec,
                frame_id,
                safe_get(msg, "latitude", ""),
                safe_get(msg, "longitude", ""),
                safe_get(msg, "altitude", ""),
                safe_get(msg, "utm_easting", ""),
                safe_get(msg, "utm_northing", ""),
                safe_get(msg, "zone", ""),
                safe_get(msg, "letter", ""),
                safe_get(msg, "hdop", ""),
                safe_get(msg, "fix_quality", ""),
                safe_get(msg, "num_satellites", ""),
                safe_get(msg, "speed", ""),
                safe_get(msg, "track", ""),
            ])
            count += 1

    print(f"Exported {count} messages to {OUT_CSV}")


if __name__ == "__main__":
    main()
