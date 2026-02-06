#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

import serial
import utm

from std_msgs.msg import Header
from gps_driver_interfaces.msg import gps_msg  # <-- your custom message


def nmea_dm_to_deg(dm: str, hemi: str) -> float:
    """
    Convert NMEA ddmm.mmmm (lat) or dddmm.mmmm (lon) to decimal degrees.
    hemi: N/S/E/W
    """
    if not dm or '.' not in dm:
        raise ValueError(f"Bad NMEA field: {dm}")

    dot = dm.find('.')
    head_len = dot - 2
    deg_str = dm[:head_len]
    min_str = dm[head_len:]

    deg = float(deg_str)
    minutes = float(min_str)
    dec = deg + (minutes / 60.0)

    if hemi in ('S', 'W'):
        dec *= -1.0
    return dec


def parse_utc_to_stamp(utc_str: str):
    """
    GPGGA UTC format: hhmmss.sss (may be hhmmss or hhmmss.ss)
    Convert to (sec, nanosec) since start of day (NOT system time).
    """
    if not utc_str:
        raise ValueError("Missing UTC time")

    # Ensure we have a float-like string
    t = float(utc_str)
    hh = int(t // 10000)
    mm = int((t - hh * 10000) // 100)
    ss = t - hh * 10000 - mm * 100  # includes fractional seconds

    sec_of_day = hh * 3600 + mm * 60 + int(ss)
    frac = ss - int(ss)
    nanosec = int(frac * 1e9)

    return sec_of_day, nanosec, t  # also return UTC as float


def parse_gpgga(line: str):
    """
    Parse $GPGGA and return:
    lat_deg, lon_deg, altitude_m, hdop, utc_float, zone_num, zone_letter, stamp_sec, stamp_nsec
    """
    line = line.strip()
    if not line.startswith("$GPGGA"):
        raise ValueError("Not GPGGA")

    core = line.split('*')[0]
    parts = core.split(',')

    # Indices (standard GPGGA):
    # 1 UTC, 2 lat, 3 N/S, 4 lon, 5 E/W, 6 fix, 7 sats, 8 hdop, 9 alt, 10 alt_units ...
    if len(parts) < 11:
        raise ValueError("Too few fields in GPGGA")

    utc_str = parts[1]
    lat_dm, lat_hemi = parts[2], parts[3]
    lon_dm, lon_hemi = parts[4], parts[5]
    fix_q = parts[6]
    hdop_str = parts[8]
    alt_str = parts[9]

    if not lat_dm or not lon_dm or not fix_q:
        raise ValueError("Missing lat/lon/fix")

    lat_deg = nmea_dm_to_deg(lat_dm, lat_hemi)
    lon_deg = nmea_dm_to_deg(lon_dm, lon_hemi)

    fix_q_int = int(fix_q)
    if fix_q_int == 0:
        raise ValueError("No fix (fix quality 0)")

    altitude = float(alt_str) if alt_str else float("nan")
    hdop = float(hdop_str) if hdop_str else float("nan")

    stamp_sec, stamp_nsec, utc_float = parse_utc_to_stamp(utc_str)

    easting, northing, zone_num, zone_letter = utm.from_latlon(lat_deg, lon_deg)

    return (
        lat_deg, lon_deg, altitude, hdop,
        easting, northing, zone_num, zone_letter,
        utc_float, stamp_sec, stamp_nsec
    )


class GpsDriverNode(Node):
    def __init__(self):
        super().__init__("gps_driver")

        self.declare_parameter("port", "/dev/pts/6")
        self.declare_parameter("baud", 4800)

        port = self.get_parameter("port").value
        baud = self.get_parameter("baud").value

        self.get_logger().info(f"Opening serial port {port} @ {baud}...")
        self.ser = serial.Serial(port, baudrate=baud, timeout=1)

        # Publish custom msg on /gps
        self.pub = self.create_publisher(gps_msg, "/gps", 10)

        self.timer = self.create_timer(0.05, self.read_loop)

    def read_loop(self):
        try:
            raw = self.ser.readline().decode(errors="ignore").strip()
            if not raw:
                return
            if not raw.startswith("$GPGGA"):
                return

            (lat, lon, alt, hdop,
             easting, northing, zone, letter,
             utc, stamp_sec, stamp_nsec) = parse_gpgga(raw)

            msg = gps_msg()

            # Header: timestamp from GPGGA time + constant frame_id
            msg.Header = Header()
            msg.Header.stamp.sec = int(stamp_sec)
            msg.Header.stamp.nanosec = int(stamp_nsec)
            msg.Header.frame_id = "GPS1_Frame"  # required constant :contentReference[oaicite:5]{index=5}

            msg.Latitude = float(lat)
            msg.Longitude = float(lon)
            msg.Altitude = float(alt)
            msg.HDOP = float(hdop)
            msg.UTM_easting = float(easting)
            msg.UTM_northing = float(northing)
            msg.UTC = float(utc)
            msg.Zone = int(zone)
            msg.Letter = str(letter)

            self.pub.publish(msg)

        except Exception as e:
            self.get_logger().warn(f"Read/parse error: {e}")


def main():
    rclpy.init()
    node = GpsDriverNode()
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
