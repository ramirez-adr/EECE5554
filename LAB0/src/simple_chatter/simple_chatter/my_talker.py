#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyTalker(Node):
    def __init__(self):
        super().__init__('my_talker')
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0, self.on_timer)
        self.count = 0

        # Anything but "hello world"
        self.base = "ros2 is cooking today"

    def on_timer(self):
        msg = String()
        msg.data = f"{self.base} [{self.count}]"
        self.pub.publish(msg)
        self.get_logger().info(f"Publishing: '{msg.data}'")
        self.count += 1


def main():
    rclpy.init()
    node = MyTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
