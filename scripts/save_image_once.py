#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageSaver(Node):
    def __init__(self, topic, output):
        super().__init__("save_image_once")
        self.bridge = CvBridge()
        self.output = Path(output)
        self.saved = False
        self.create_subscription(Image, topic, self.callback, 10)

    def callback(self, msg):
        if self.saved:
            return
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(self.output), image)
        self.get_logger().info(f"saved image to {self.output}")
        self.saved = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="/camera/image_raw")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    rclpy.init()
    node = ImageSaver(args.topic, args.output)
    deadline = time.monotonic() + args.timeout
    try:
        while rclpy.ok() and not node.saved and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

    if not node.saved:
        print(f"failed to receive image on {args.topic}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
