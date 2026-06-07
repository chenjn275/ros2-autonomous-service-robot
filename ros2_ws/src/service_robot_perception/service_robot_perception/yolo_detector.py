import json
from pathlib import Path

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class YoloDetector(Node):
    def __init__(self):
        super().__init__("yolo_detector")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("detections_topic", "/perception/yolo/detections")
        self.declare_parameter("annotated_topic", "/perception/yolo/annotated")
        self.declare_parameter("model_path", "")
        self.declare_parameter("confidence", 0.25)

        image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        detections_topic = self.get_parameter("detections_topic").get_parameter_value().string_value
        annotated_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value
        self.model_path = self.get_parameter("model_path").get_parameter_value().string_value
        self.confidence = self.get_parameter("confidence").get_parameter_value().double_value

        self.bridge = CvBridge()
        self.model = self._load_model(self.model_path)
        self.detections_pub = self.create_publisher(String, detections_topic, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)
        self.subscription = self.create_subscription(Image, image_topic, self.image_callback, 10)
        self.get_logger().info(f"YOLO detector subscribing to {image_topic}")

    def _load_model(self, model_path):
        if not model_path:
            self.get_logger().info("No model_path configured; running in no-model mode.")
            return None
        if not Path(model_path).is_file():
            self.get_logger().warning(f"model_path does not exist: {model_path}; using no-model mode.")
            return None
        try:
            from ultralytics import YOLO
        except ImportError:
            self.get_logger().warning("ultralytics is not installed; using no-model mode.")
            return None
        return YOLO(model_path)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        detections = []

        if self.model is not None:
            results = self.model.predict(frame, conf=self.confidence, verbose=False)
            for result in results:
                names = result.names
                for box in result.boxes:
                    xyxy = [float(v) for v in box.xyxy[0].tolist()]
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = names.get(class_id, str(class_id))
                    detections.append(
                        {
                            "class_id": class_id,
                            "label": label,
                            "confidence": confidence,
                            "bbox_xyxy": xyxy,
                        }
                    )
                    x1, y1, x2, y2 = [int(v) for v in xyxy]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 255), 2)
                    cv2.putText(
                        frame,
                        f"{label} {confidence:.2f}",
                        (x1, max(0, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 180, 255),
                        1,
                        cv2.LINE_AA,
                    )

        result_msg = String()
        result_msg.data = json.dumps({"detections": detections}, ensure_ascii=True)
        self.detections_pub.publish(result_msg)
        self.annotated_pub.publish(self.bridge.cv2_to_imgmsg(frame, encoding="bgr8"))


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
