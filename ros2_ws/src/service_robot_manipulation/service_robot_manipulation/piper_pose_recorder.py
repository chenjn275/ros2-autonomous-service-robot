from pathlib import Path
from typing import Any

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import yaml


DEFAULT_SOURCE_CONFIG = (
    Path.home()
    / "ros2-autonomous-service-robot"
    / "ros2_ws"
    / "src"
    / "service_robot_manipulation"
    / "config"
    / "piper_pick_place_sequences.yaml"
)


class PiperPoseRecorder(Node):
    def __init__(self) -> None:
        super().__init__("piper_pose_recorder")
        self.declare_parameter("pose_name", "")
        self.declare_parameter("config_path", str(DEFAULT_SOURCE_CONFIG))
        self.declare_parameter("state_topic", "/joint_states_feedback")
        self.declare_parameter(
            "joint_names",
            ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7"],
        )
        self.declare_parameter("mark_calibrated", False)
        self.declare_parameter("timeout_sec", 5.0)

        self.pose_name = self.get_parameter("pose_name").get_parameter_value().string_value.strip()
        self.config_path = Path(
            self.get_parameter("config_path").get_parameter_value().string_value
        ).expanduser()
        self.state_topic = self.get_parameter("state_topic").get_parameter_value().string_value
        self.joint_names = list(
            self.get_parameter("joint_names").get_parameter_value().string_array_value
        )
        self.mark_calibrated = self.get_parameter("mark_calibrated").get_parameter_value().bool_value
        self.timeout_sec = self.get_parameter("timeout_sec").get_parameter_value().double_value

        self.latest_state: JointState | None = None
        self.create_subscription(JointState, self.state_topic, self._on_joint_state, 10)

    def _on_joint_state(self, msg: JointState) -> None:
        self.latest_state = msg

    def record_once(self) -> bool:
        if not self.pose_name:
            self.get_logger().error("pose_name is required.")
            return False

        deadline = self.get_clock().now().nanoseconds / 1e9 + max(self.timeout_sec, 0.0)
        self.get_logger().info(f"Waiting for joint state on {self.state_topic}")
        while rclpy.ok() and self.latest_state is None:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.get_clock().now().nanoseconds / 1e9 > deadline:
                self.get_logger().error(f"Timed out waiting for {self.state_topic}")
                return False

        state = self.latest_state
        if state is None:
            return False

        state_map = {
            name: float(state.position[index])
            for index, name in enumerate(state.name)
            if index < len(state.position)
        }
        missing = [name for name in self.joint_names if name not in state_map]
        if missing:
            self.get_logger().error(f"Missing joints in feedback: {missing}")
            return False

        data = self._load_config()
        data.setdefault("metadata", {})
        data.setdefault("poses", {})
        data["poses"][self.pose_name] = {
            "placeholder": False,
            "positions": {name: state_map[name] for name in self.joint_names}
        }
        if self.mark_calibrated:
            data["metadata"]["calibrated"] = True

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)

        self.get_logger().info(
            f"Recorded pose '{self.pose_name}' to {self.config_path}"
            + (" and marked config calibrated." if self.mark_calibrated else ".")
        )
        return True

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with self.config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        return data if isinstance(data, dict) else {}


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PiperPoseRecorder()
    try:
        ok = node.record_once()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
