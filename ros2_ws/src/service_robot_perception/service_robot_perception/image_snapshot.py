from pathlib import Path

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageSnapshot(Node):
    def __init__(self):
        super().__init__("image_snapshot")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("output_path", "/tmp/craic2026_snapshot.png")

        self.output_path = Path(str(self.get_parameter("output_path").value)).expanduser()
        self.bridge = CvBridge()
        image_topic = str(self.get_parameter("image_topic").value)
        self.subscription = self.create_subscription(Image, image_topic, self.image_callback, 10)
        self.get_logger().info(f"Waiting for one image on {image_topic}")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(self.output_path), frame):
            self.get_logger().error(f"Failed to write image: {self.output_path}")
        else:
            self.get_logger().info(f"Saved image: {self.output_path}")
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = ImageSnapshot()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
