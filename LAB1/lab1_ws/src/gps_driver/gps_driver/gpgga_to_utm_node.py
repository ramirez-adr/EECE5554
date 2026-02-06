#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import utm


def nmea_dm_to_deg(dm: str, hemi: str) -> float:
    """
    Convert NMEA ddmm.mmmm (lat) or dddmm.mmmm (lon) to decimal degrees.
    hemi: N/S/E/W
    """
    if not dm or '.' not in dm:
        raise ValueError(f"Bad NMEA field: {dm}")

    # Split degrees/minutes based on lat vs lon length
    # lat: ddmm.mmmm -> degrees are first 2
    # lon: dddmm.mmmm -> degrees are first 3
    dot = dm.find('.')
    head_len = dot - 2  # everything before last 2 digits of minutes
    deg_str = dm[:head_len]
    min_str = dm[head_len:]

    deg = float(deg_str)
    minutes = float(min_str)

    dec = deg + (minutes / 60.0)

    if hemi in ('S', 'W'):
        dec *= -1.0
    return dec


def parse_gpgga(line: str):
    """
    Parse a $GPGGA sentence and return (lat_deg, lon_deg, fix_quality).
    Raises ValueError if not parseable.
    """
    line = line.strip()
    if not line.startswith("$GPGGA"):
        raise ValueError("Not GPGGA")

    # Remove checksum part for easier splitting
    core = line.split('*')[0]
    parts = core.split(',')

    # GPGGA fields we need:
    # 0:$GPGGA, 1:time, 2:lat, 3:N/S, 4:lon, 5:E/W, 6:fix quality, ...
    if len(parts) < 7:
        raise ValueError("Too few fields")

    lat_dm = parts[2]
    lat_hemi = parts[3]
    lon_dm = parts[4]
    lon_hemi = parts[5]
    fix_q = parts[6]

    if not lat_dm or not lon_dm or not fix_q:
        raise ValueError("Missing fields")

    lat_deg = nmea_dm_to_deg(lat_dm, lat_hemi)
    lon_deg = nmea_dm_to_deg(lon_dm, lon_hemi)

    return lat_deg, lon_deg, int(fix_q)


class GpggaToUtmNode(Node):
    def __init__(self):
        super().__init__("gpgga_to_utm")

        # Parameters (set these when you run the node)
        self.declare_parameter("port", "/dev/pts/6")   # emulator prints this
        self.declare_parameter("baud", 4800)

        port = self.get_parameter("port").get_parameter_value().string_value
        baud = self.get_parameter("baud").get_parameter_value().integer_value

        self.get_logger().info(f"Opening serial port {port} @ {baud}...")
        self.ser = serial.Serial(port, baudrate=baud, timeout=1)

        self.pub = self.create_publisher(String, "gps/utm", 10)

        # Timer to poll serial
        self.timer = self.create_timer(0.05, self.read_loop)  # 20 Hz-ish

    def read_loop(self):
        try:
            raw = self.ser.readline().decode(errors="ignore").strip()
            if not raw:
                return

            if raw.startswith("$GPGGA"):
                lat, lon, fix_q = parse_gpgga(raw)

                # Only publish if fix quality indicates a fix (0 = invalid)
                if fix_q == 0:
                    self.get_logger().warn("No GPS fix (fix quality 0)")
                    return

                easting, northing, zone_num, zone_letter = utm.from_latlon(lat, lon)

                msg = String()
                msg.data = (
                    f"UTM: E={easting:.3f} N={northing:.3f} "
                    f"Zone={zone_num}{zone_letter}  "
                    f"lat={lat:.6f} lon={lon:.6f}  fix={fix_q}"
                )
                self.pub.publish(msg)

        except Exception as e:
            self.get_logger().warn(f"Read/parse error: {e}")


def main():
    rclpy.init()
    node = GpggaToUtmNode()
    try:
        rclpy.spin(node)
    finally:
        try:
            node.ser.close()
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
