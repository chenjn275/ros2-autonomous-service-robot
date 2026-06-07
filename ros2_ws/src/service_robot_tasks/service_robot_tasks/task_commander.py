import json
import math
import time
from pathlib import Path

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String
import yaml


def quaternion_from_yaw(yaw):
    half = yaw * 0.5
    return {
        "x": 0.0,
        "y": 0.0,
        "z": math.sin(half),
        "w": math.cos(half),
    }


class TaskCommander(Node):
    def __init__(self):
        super().__init__("task_commander")
        self.declare_parameter("mission_config", "")
        self.declare_parameter("use_nav", False)
        self.declare_parameter("mock_nav_delay_sec", 0.5)
        self.declare_parameter("default_nav_timeout_sec", 20.0)
        self.declare_parameter("nav_server_wait_sec", 30.0)
        self.declare_parameter("nav_goal_send_timeout_sec", 30.0)
        self.declare_parameter("start_delay_sec", 1.0)

        self.mission_config = self.get_parameter("mission_config").get_parameter_value().string_value
        self.use_nav = self.get_parameter("use_nav").get_parameter_value().bool_value
        self.mock_nav_delay_sec = (
            self.get_parameter("mock_nav_delay_sec").get_parameter_value().double_value
        )
        self.default_nav_timeout_sec = (
            self.get_parameter("default_nav_timeout_sec").get_parameter_value().double_value
        )
        self.nav_server_wait_sec = (
            self.get_parameter("nav_server_wait_sec").get_parameter_value().double_value
        )
        self.nav_goal_send_timeout_sec = (
            self.get_parameter("nav_goal_send_timeout_sec").get_parameter_value().double_value
        )
        self.start_delay_sec = (
            self.get_parameter("start_delay_sec").get_parameter_value().double_value
        )

        self.latest_qr = None
        self.latest_yolo = None
        self.create_subscription(String, "/perception/qr/result", self.qr_callback, 10)
        self.create_subscription(String, "/perception/yolo/detections", self.yolo_callback, 10)
        self.status_pub = self.create_publisher(String, "/tasks/status", 10)
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.started = False
        self.timer = self.create_timer(self.start_delay_sec, self.start_once)

    def qr_callback(self, msg):
        self.latest_qr = self._safe_json(msg.data)

    def yolo_callback(self, msg):
        self.latest_yolo = self._safe_json(msg.data)

    def start_once(self):
        if self.started:
            return
        self.started = True
        self.timer.cancel()
        self.run_mission()

    def run_mission(self):
        mission = self.load_mission()
        mission_id = mission.get("mission", {}).get("id", "unnamed_mission")
        self.publish_status("mission_started", {"mission_id": mission_id})

        for waypoint in mission.get("waypoints", []):
            self.handle_waypoint(waypoint)

        self.publish_status("mission_finished", {"mission_id": mission_id})
        self.get_logger().info(f"Mission finished: {mission_id}")

    def load_mission(self):
        path = Path(self.mission_config)
        if not path.is_file():
            raise FileNotFoundError(f"mission_config does not exist: {path}")
        with path.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream) or {}

    def handle_waypoint(self, waypoint):
        name = waypoint.get("name", "unnamed_waypoint")
        self.publish_status("waypoint_started", {"name": name})

        if not waypoint.get("skip_navigation", False):
            self.navigate(waypoint)
        else:
            self.get_logger().info(f"Skip navigation for waypoint: {name}")

        for task in waypoint.get("tasks", []):
            self.handle_task(task)

        self.publish_status("waypoint_finished", {"name": name})

    def navigate(self, waypoint):
        if not self.use_nav:
            self.get_logger().info(f"Mock navigation to {waypoint.get('name', 'waypoint')}")
            time.sleep(self.mock_nav_delay_sec)
            return

        if not self.nav_client.wait_for_server(timeout_sec=self.nav_server_wait_sec):
            self.publish_status(
                "navigation_unavailable",
                {"waypoint": waypoint.get("name", "waypoint")},
            )
            return

        goal = NavigateToPose.Goal()
        goal.pose = self.make_pose(waypoint)
        future = self.nav_client.send_goal_async(goal)
        send_deadline = time.monotonic() + self.nav_goal_send_timeout_sec
        while rclpy.ok() and not future.done():
            if time.monotonic() >= send_deadline:
                self.publish_status(
                    "navigation_send_timeout",
                    {"waypoint": waypoint.get("name", "")},
                )
                return
            rclpy.spin_once(self, timeout_sec=0.1)

        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            self.publish_status("navigation_rejected", {"waypoint": waypoint.get("name", "")})
            return

        result_future = goal_handle.get_result_async()
        timeout_sec = float(waypoint.get("nav_timeout_sec", self.default_nav_timeout_sec))
        deadline = time.monotonic() + timeout_sec
        while rclpy.ok() and not result_future.done():
            if time.monotonic() >= deadline:
                goal_handle.cancel_goal_async()
                self.publish_status(
                    "navigation_timeout",
                    {"waypoint": waypoint.get("name", ""), "timeout_sec": timeout_sec},
                )
                return
            rclpy.spin_once(self, timeout_sec=0.1)

        result = result_future.result()
        status = getattr(result, "status", None)
        self.publish_status(
            "navigation_finished",
            {"waypoint": waypoint.get("name", ""), "status": status},
        )

    def make_pose(self, waypoint):
        pose = PoseStamped()
        pose.header.frame_id = waypoint.get("frame_id", "map")
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(waypoint.get("x", 0.0))
        pose.pose.position.y = float(waypoint.get("y", 0.0))
        pose.pose.position.z = 0.0
        quat = quaternion_from_yaw(float(waypoint.get("yaw", 0.0)))
        pose.pose.orientation.x = quat["x"]
        pose.pose.orientation.y = quat["y"]
        pose.pose.orientation.z = quat["z"]
        pose.pose.orientation.w = quat["w"]
        return pose

    def handle_task(self, task):
        task_type = task.get("type", "unknown")
        name = task.get("name", task_type)
        self.publish_status("task_started", {"name": name, "type": task_type})

        if task_type == "wait":
            time.sleep(float(task.get("seconds", 0.5)))
        elif task_type == "observe_qr":
            self.publish_status("qr_snapshot", {"latest_qr": self.latest_qr})
        elif task_type == "observe_yolo":
            self.publish_status("yolo_snapshot", {"latest_yolo": self.latest_yolo})
        elif task_type == "classify":
            category = self.infer_category(task)
            self.publish_status("classification_result", {"category": category})
        elif task_type == "place_mock":
            self.publish_status("mock_place", {"bin": task.get("bin", "unknown")})
        else:
            self.publish_status("task_skipped", {"name": name, "type": task_type})

        self.publish_status("task_finished", {"name": name, "type": task_type})

    def infer_category(self, task):
        detections = []
        if isinstance(self.latest_yolo, dict):
            detections = self.latest_yolo.get("detections", [])
        if detections:
            first = detections[0]
            return first.get("label", str(first.get("class_id", "unknown")))
        return task.get("fallback_category", "unknown")

    def publish_status(self, state, data=None):
        payload = {"state": state, "data": data or {}}
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=True)
        self.status_pub.publish(msg)
        self.get_logger().info(msg.data)

    @staticmethod
    def _safe_json(data):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"raw": data}


def main(args=None):
    rclpy.init(args=args)
    node = TaskCommander()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
