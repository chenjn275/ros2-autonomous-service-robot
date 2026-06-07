import json

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class QrDetector(Node):
    def __init__(self):
        super().__init__("qr_detector")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("result_topic", "/perception/qr/result")
        self.declare_parameter("annotated_topic", "/perception/qr/annotated")

        image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        result_topic = self.get_parameter("result_topic").get_parameter_value().string_value
        annotated_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value

        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()
        self.result_pub = self.create_publisher(String, result_topic, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)
        self.subscription = self.create_subscription(Image, image_topic, self.image_callback, 10)
        self.get_logger().info(f"QR detector subscribing to {image_topic}")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        detections = []

        ok, decoded_info, points, _ = self.detector.detectAndDecodeMulti(frame)
        if ok and points is not None:
            for text, corners in zip(decoded_info, points):
                if not text:
                    continue
                polygon = corners.astype(int).tolist()
                detections.append({"text": text, "polygon": polygon})
                pts = corners.astype(int).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    text,
                    tuple(pts[0][0]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )
        else:
            text, points, _ = self.detector.detectAndDecode(frame)
            if text and points is not None:
                polygon = points.astype(int).tolist()
                detections.append({"text": text, "polygon": polygon})
                pts = points.astype(int).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

        result = String()
        result.data = json.dumps({"detections": detections}, ensure_ascii=True)
        self.result_pub.publish(result)
        self.annotated_pub.publish(self.bridge.cv2_to_imgmsg(frame, encoding="bgr8"))


def main(args=None):
    rclpy.init(args=args)
    node = QrDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
