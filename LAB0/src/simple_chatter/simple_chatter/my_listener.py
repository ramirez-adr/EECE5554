#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def modify_text(s: str) -> str:
    # Slight modification: swap first two characters (if possible) and append "!"
    if len(s) >= 2:
        s = s[1] + s[0] + s[2:]
    return s + "!"


class MyListener(Node):
    def __init__(self):
        super().__init__('my_listener')
        self.sub = self.create_subscription(String, 'chatter', self.cb, 10)

    def cb(self, msg: String):
        modified = modify_text(msg.data)
        self.get_logger().info(f"I heard {modified}")


def main():
    rclpy.init()
    node = MyListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
