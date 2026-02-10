#!/usr/bin/env python3
import argparse
import serial
import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from rtk_driver_msgs.msg import CustomRTK
import utm


def nmea_to_decimal(dm: str, hemi: str) -> float:
    if dm == '' or hemi == '':
        raise ValueError("Empty lat/lon field")

    raw = float(dm)
    deg = int(raw // 100)
    minutes = raw - deg * 100
    dec = deg + minutes / 60.0

    if hemi in ('S', 'W'):
        dec *= -1.0
    return dec


def parse_gngga(sentence: str):
    """
    Parse $GNGGA (and accept $GPGGA just in case).
    Extract utc, lat, lon, alt, fix_quality, hdop, and raw gngga string.
    """
    if not (sentence.startswith("$GNGGA") or sentence.startswith("$GPGGA")):
        return None

    raw_sentence = sentence.strip()

    body = raw_sentence.split('*')[0]
    fields = body.split(',')

    if len(fields) < 10:
        return None

    utc = fields[1]
    lat_dm, lat_hemi = fields[2], fields[3]
    lon_dm, lon_hemi = fields[4], fields[5]
    fix_quality_str = fields[6]
    hdop_str = fields[8]
    alt_str = fields[9]

    if fix_quality_str == '' or fix_quality_str == '0':
        return None

    lat = nmea_to_decimal(lat_dm, lat_hemi)
    lon = nmea_to_decimal(lon_dm, lon_hemi)

    altitude = float(alt_str) if alt_str != '' else float('nan')
    fix_quality = int(fix_quality_str) if fix_quality_str != '' else 0
    hdop = float(hdop_str) if hdop_str != '' else float('nan')

    easting, northing, zone_num, zone_letter = utm.from_latlon(lat, lon)

    return {
        "utc": utc,
        "lat": lat,
        "lon": lon,
        "alt": altitude,
        "fix_quality": fix_quality,
        "hdop": hdop,
        "gngga": raw_sentence,
        "easting": float(easting),
        "northing": float(northing),
        "zone": str(zone_num),
        "letter": str(zone_letter),
    }


def gga_utc_to_ros_time(utc_str: str):
    if not utc_str or len(utc_str) < 6:
        return (0, 0)

    hh = int(utc_str[0:2])
    mm = int(utc_str[2:4])
    ss = float(utc_str[4:])

    total = hh * 3600 + mm * 60 + ss
    sec = int(total)
    nsec = int((total - sec) * 1e9)
    return (sec, nsec)


class RTKDriver(Node):
    def __init__(self, port: str, baud: int = 4800):
        super().__init__('rtk_driver')
        self.publisher_ = self.create_publisher(CustomRTK, '/rtk', 10)

        self.ser = serial.Serial(port, baudrate=baud, timeout=1.0)
        self.get_logger().info(f"Reading RTK GNSS on {port} @ {baud} baud")

        self.timer = self.create_timer(0.05, self.read_once)

    def read_once(self):
        try:
            line = self.ser.readline().decode('ascii', errors='ignore').strip()
            if not line:
                return

            parsed = parse_gngga(line)
            if parsed is None:
                return

            msg = CustomRTK()

            hdr = Header()
            hdr.frame_id = "GPS1_Frame"
            sec, nsec = gga_utc_to_ros_time(parsed["utc"])
            hdr.stamp.sec = sec
            hdr.stamp.nanosec = nsec
            msg.header = hdr

            msg.latitude = parsed["lat"]
            msg.longitude = parsed["lon"]
            msg.altitude = parsed["alt"]

            msg.utm_easting = parsed["easting"]
            msg.utm_northing = parsed["northing"]
            msg.zone = parsed["zone"]
            msg.letter = parsed["letter"]

            msg.utc = parsed["utc"]
            msg.gngga = parsed["gngga"]
            msg.fix_quality = parsed["fix_quality"]
            msg.hdop = parsed["hdop"]

            self.publisher_.publish(msg)

        except Exception as e:
            self.get_logger().warn(f"Read/parse error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', required=True, help='Serial port, e.g. /dev/ttyUSB2 or /dev/pts/X')
    parser.add_argument('--baud', '-b', type=int, default=4800)
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = RTKDriver(port=args.port, baud=args.baud)
    try:
        rclpy.spin(node)
    finally:
        try:
            node.ser.close()
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
