import json
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
from cv_bridge import CvBridge
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import yaml

try:
    from ament_index_python.packages import get_package_share_directory
except ImportError:  # pragma: no cover - available in ROS runtime
    get_package_share_directory = None


@dataclass(frozen=True)
class MarkerTemplate:
    marker_id: str
    label: str
    place_zone: str
    image: np.ndarray


def order_quad_points(points):
    pts = np.asarray(points, dtype=np.float32).reshape(4, 2)
    ordered = np.zeros((4, 2), dtype=np.float32)
    point_sum = pts.sum(axis=1)
    point_diff = np.diff(pts, axis=1).reshape(4)
    ordered[0] = pts[np.argmin(point_sum)]
    ordered[2] = pts[np.argmax(point_sum)]
    ordered[1] = pts[np.argmin(point_diff)]
    ordered[3] = pts[np.argmax(point_diff)]
    return ordered


def pattern_to_image(pattern, size):
    rows = [str(row).strip() for row in pattern if str(row).strip()]
    if not rows:
        raise ValueError("empty marker pattern")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("marker pattern rows must have equal width")

    grid = np.zeros((len(rows), width), dtype=np.uint8)
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            if value not in ("0", "1"):
                raise ValueError("marker pattern must contain only 0 and 1")
            grid[y, x] = 255 if value == "1" else 0
    return cv2.resize(grid, (size, size), interpolation=cv2.INTER_NEAREST)


def normalize_marker_image(image, size):
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    gray = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # The competition markers are white modules on a mostly black square.
    if float(binary.mean()) > 127.0:
        binary = cv2.bitwise_not(binary)
    return binary


def marker_score(candidate, template):
    cand = candidate > 127
    tmpl = template > 127
    return float(np.count_nonzero(cand == tmpl)) / float(cand.size)


class CustomMarkerDetector(Node):
    def __init__(self):
        super().__init__("custom_marker_detector")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("result_topic", "/perception/custom_marker/result")
        self.declare_parameter("annotated_topic", "/perception/custom_marker/annotated")
        self.declare_parameter("templates_config", "")
        self.declare_parameter("template_size", 96)
        self.declare_parameter("black_threshold", 90)
        self.declare_parameter("min_area", 900.0)
        self.declare_parameter("max_area_ratio", 0.45)
        self.declare_parameter("min_square_ratio", 0.55)
        self.declare_parameter("max_square_ratio", 1.45)
        self.declare_parameter("match_threshold", 0.72)
        self.declare_parameter("save_unknown_candidates", False)
        self.declare_parameter("candidate_save_dir", "/tmp/craic2026_marker_candidates")

        self.template_size = int(self.get_parameter("template_size").value)
        self.black_threshold = int(self.get_parameter("black_threshold").value)
        self.min_area = float(self.get_parameter("min_area").value)
        self.max_area_ratio = float(self.get_parameter("max_area_ratio").value)
        self.min_square_ratio = float(self.get_parameter("min_square_ratio").value)
        self.max_square_ratio = float(self.get_parameter("max_square_ratio").value)
        self.match_threshold = float(self.get_parameter("match_threshold").value)
        self.save_unknown_candidates = bool(
            self.get_parameter("save_unknown_candidates").value
        )
        self.candidate_save_dir = Path(str(self.get_parameter("candidate_save_dir").value))

        config_path = self._resolve_templates_config()
        self.templates = self._load_templates(config_path)

        image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        result_topic = self.get_parameter("result_topic").get_parameter_value().string_value
        annotated_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value

        self.bridge = CvBridge()
        self.result_pub = self.create_publisher(String, result_topic, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)
        self.subscription = self.create_subscription(Image, image_topic, self.image_callback, 10)
        self.get_logger().info(
            f"Custom marker detector subscribing to {image_topic}; "
            f"loaded {len(self.templates)} template(s)"
        )

    def _resolve_templates_config(self):
        configured = str(self.get_parameter("templates_config").value).strip()
        if configured:
            return Path(configured).expanduser()
        if get_package_share_directory is None:
            return Path("config/custom_markers.yaml")
        return Path(get_package_share_directory("service_robot_perception")) / "config" / "custom_markers.yaml"

    def _load_templates(self, config_path):
        if not config_path.is_file():
            self.get_logger().warning(f"Marker template config does not exist: {config_path}")
            return []
        with config_path.open("r", encoding="utf-8") as stream:
            config = yaml.safe_load(stream) or {}

        templates = []
        base_dir = config_path.parent
        for item in config.get("markers", []):
            try:
                marker_id = str(item["id"])
                label = str(item.get("label", marker_id))
                place_zone = str(item.get("place_zone", ""))
                if item.get("template_path"):
                    path = Path(str(item["template_path"]))
                    if not path.is_absolute():
                        path = base_dir / path
                    raw = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                    if raw is None:
                        raise ValueError(f"failed to read template image: {path}")
                    image = normalize_marker_image(raw, self.template_size)
                else:
                    image = pattern_to_image(item.get("pattern", []), self.template_size)
                templates.append(MarkerTemplate(marker_id, label, place_zone, image))
            except Exception as exc:
                self.get_logger().warning(f"Skipping invalid marker template {item}: {exc}")
        return templates

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        detections = []
        if self.templates:
            for candidate in self._find_candidates(frame):
                detection = self._match_candidate(candidate)
                if detection is None:
                    self._save_unknown(candidate["warp"])
                    continue
                detections.append(detection)
                self._draw_detection(frame, detection)

        result = String()
        result.data = json.dumps(
            {"detections": detections, "best": detections[0] if detections else None},
            ensure_ascii=True,
        )
        self.result_pub.publish(result)
        self.annotated_pub.publish(self.bridge.cv2_to_imgmsg(frame, encoding="bgr8"))

    def _find_candidates(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.black_threshold > 0:
            _, mask = cv2.threshold(gray, self.black_threshold, 255, cv2.THRESH_BINARY_INV)
        else:
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((5, 5), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        frame_area = float(frame.shape[0] * frame.shape[1])
        candidates = []
        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < self.min_area or area > frame_area * self.max_area_ratio:
                continue

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            if len(approx) == 4:
                quad = approx.reshape(4, 2)
            else:
                rect = cv2.minAreaRect(contour)
                quad = cv2.boxPoints(rect)

            rect = cv2.minAreaRect(quad.astype(np.float32))
            width, height = rect[1]
            if min(width, height) <= 1.0:
                continue
            ratio = max(width, height) / min(width, height)
            if ratio < self.min_square_ratio or ratio > self.max_square_ratio:
                continue

            ordered = order_quad_points(quad)
            dst = np.array(
                [
                    [0, 0],
                    [self.template_size - 1, 0],
                    [self.template_size - 1, self.template_size - 1],
                    [0, self.template_size - 1],
                ],
                dtype=np.float32,
            )
            transform = cv2.getPerspectiveTransform(ordered, dst)
            warp = cv2.warpPerspective(frame, transform, (self.template_size, self.template_size))
            normalized = normalize_marker_image(warp, self.template_size)
            candidates.append({"polygon": ordered.astype(int).tolist(), "warp": normalized})
        return candidates

    def _match_candidate(self, candidate):
        best = None
        best_score = 0.0
        best_rotation = 0
        for template in self.templates:
            for rotation in range(4):
                rotated = np.rot90(candidate["warp"], rotation)
                score = marker_score(rotated, template.image)
                if score > best_score:
                    best = template
                    best_score = score
                    best_rotation = rotation * 90

        if best is None or best_score < self.match_threshold:
            return None
        return {
            "id": best.marker_id,
            "label": best.label,
            "place_zone": best.place_zone,
            "score": round(best_score, 4),
            "rotation_deg": best_rotation,
            "polygon": candidate["polygon"],
        }

    def _draw_detection(self, frame, detection):
        pts = np.asarray(detection["polygon"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        text = f"{detection['id']} {detection['label']} {detection['score']:.2f}"
        cv2.putText(
            frame,
            text,
            tuple(pts[0][0]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    def _save_unknown(self, image):
        if not self.save_unknown_candidates:
            return
        self.candidate_save_dir.mkdir(parents=True, exist_ok=True)
        path = self.candidate_save_dir / f"candidate_{time.time_ns()}.png"
        cv2.imwrite(str(path), image)


def main(args=None):
    rclpy.init(args=args)
    node = CustomMarkerDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
