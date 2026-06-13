import threading
import time
from pathlib import Path
from typing import Any

from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger
import yaml


def default_config_path() -> str:
    source_config = (
        Path.home()
        / "ros2-autonomous-service-robot"
        / "ros2_ws"
        / "src"
        / "service_robot_manipulation"
        / "config"
        / "piper_pick_place_sequences.yaml"
    )
    if source_config.exists():
        return str(source_config)
    return str(
        Path(get_package_share_directory("service_robot_manipulation"))
        / "config"
        / "piper_pick_place_sequences.yaml"
    )


class PiperSequenceExecutor(Node):
    def __init__(self) -> None:
        super().__init__("piper_sequence_executor")
        self.declare_parameter("config_path", default_config_path())
        self.declare_parameter("command_topic", "/joint_command")
        self.declare_parameter("state_topic", "/joint_states_feedback")
        self.declare_parameter("service_prefix", "/manipulation/piper")
        self.declare_parameter("require_calibrated", True)
        self.declare_parameter("dry_run", False)
        self.declare_parameter("publish_hz", 10.0)
        self.declare_parameter("state_timeout_sec", 3.0)
        self.declare_parameter("position_tolerance", 0.05)
        self.declare_parameter("gripper_tolerance", 0.01)

        self.config_path = Path(
            self.get_parameter("config_path").get_parameter_value().string_value
        ).expanduser()
        self.command_topic = self.get_parameter("command_topic").get_parameter_value().string_value
        self.state_topic = self.get_parameter("state_topic").get_parameter_value().string_value
        self.service_prefix = (
            self.get_parameter("service_prefix").get_parameter_value().string_value.rstrip("/")
        )
        self.require_calibrated = (
            self.get_parameter("require_calibrated").get_parameter_value().bool_value
        )
        self.dry_run = self.get_parameter("dry_run").get_parameter_value().bool_value
        self.publish_hz = self.get_parameter("publish_hz").get_parameter_value().double_value
        self.state_timeout_sec = (
            self.get_parameter("state_timeout_sec").get_parameter_value().double_value
        )
        self.position_tolerance = (
            self.get_parameter("position_tolerance").get_parameter_value().double_value
        )
        self.gripper_tolerance = (
            self.get_parameter("gripper_tolerance").get_parameter_value().double_value
        )

        self.callback_group = ReentrantCallbackGroup()
        self.command_pub = self.create_publisher(JointState, self.command_topic, 10)
        self.latest_state: JointState | None = None
        self.state_lock = threading.Lock()
        self.execute_lock = threading.Lock()

        self.create_subscription(
            JointState,
            self.state_topic,
            self._on_joint_state,
            10,
            callback_group=self.callback_group,
        )

        self.config = self._load_config()
        self._sequence_services = []
        self._create_services()
        self.get_logger().info(
            f"Piper sequence executor ready. config={self.config_path} "
            f"services={sorted(self.config.get('sequences', {}).keys())} dry_run={self.dry_run}"
        )

    def _on_joint_state(self, msg: JointState) -> None:
        with self.state_lock:
            self.latest_state = msg

    def _create_services(self) -> None:
        self._sequence_services.append(
            self.create_service(
                Trigger,
                f"{self.service_prefix}/reload",
                self._reload_callback,
                callback_group=self.callback_group,
            )
        )
        for sequence_name in sorted(self.config.get("sequences", {})):
            self._sequence_services.append(
                self.create_service(
                    Trigger,
                    f"{self.service_prefix}/{sequence_name}",
                    self._make_sequence_callback(sequence_name),
                    callback_group=self.callback_group,
                )
            )

    def _reload_callback(self, request, response):
        del request
        self.config = self._load_config()
        response.success = True
        response.message = f"Reloaded {self.config_path}"
        return response

    def _make_sequence_callback(self, sequence_name: str):
        def callback(request, response):
            del request
            ok, message = self.execute_sequence(sequence_name)
            response.success = ok
            response.message = message
            return response

        return callback

    def execute_sequence(self, sequence_name: str) -> tuple[bool, str]:
        if not self.execute_lock.acquire(blocking=False):
            return False, "another Piper sequence is already running"
        try:
            return self._execute_sequence_locked(sequence_name)
        finally:
            self.execute_lock.release()

    def _execute_sequence_locked(self, sequence_name: str) -> tuple[bool, str]:
        self.config = self._load_config()
        metadata = self.config.get("metadata", {})
        if self.require_calibrated and not bool(metadata.get("calibrated", False)):
            return False, (
                f"{self.config_path} is not calibrated. Record real poses and set "
                "metadata.calibrated: true before running with require_calibrated."
            )

        sequences = self.config.get("sequences", {})
        sequence = sequences.get(sequence_name)
        if not isinstance(sequence, list) or not sequence:
            return False, f"sequence '{sequence_name}' is missing or empty"

        if not self.dry_run and self._wait_for_state(self.state_timeout_sec) is None:
            return False, f"no joint feedback on {self.state_topic}"

        self.get_logger().info(f"Executing Piper sequence: {sequence_name}")
        for index, step in enumerate(sequence):
            ok, message = self._execute_step(step, index)
            if not ok:
                return False, f"{sequence_name} step {index + 1} failed: {message}"
        return True, f"sequence '{sequence_name}' completed"

    def _execute_step(self, step: Any, index: int) -> tuple[bool, str]:
        if not isinstance(step, dict):
            return False, "step must be a mapping"
        wait_sec = float(step.get("wait_sec", 0.0))
        if wait_sec > 0.0:
            time.sleep(wait_sec)
            return True, "waited"

        command = self._build_command(step)
        duration_sec = float(
            step.get(
                "duration_sec",
                self.config.get("settings", {}).get("default_duration_sec", 2.0),
            )
        )
        settle_sec = float(step.get("settle_sec", 0.0))

        if self.dry_run:
            self.get_logger().info(
                f"[DRY RUN] step {index + 1}: names={command.name} "
                f"positions={[round(value, 4) for value in command.position]} "
                f"duration={duration_sec:.2f}s"
            )
            time.sleep(min(duration_sec + settle_sec, 0.1))
            return True, "dry run"

        period = 1.0 / max(self.publish_hz, 1.0)
        deadline = time.monotonic() + max(duration_sec, period)
        while rclpy.ok() and time.monotonic() <= deadline:
            command.header.stamp = self.get_clock().now().to_msg()
            self.command_pub.publish(command)
            time.sleep(period)

        if settle_sec > 0.0:
            time.sleep(settle_sec)

        if bool(step.get("wait_until_reached", True)):
            timeout_sec = float(step.get("reach_timeout_sec", max(1.0, duration_sec + 2.0)))
            if not self._wait_until_reached(command, timeout_sec):
                return False, "target not reached within tolerance"
        return True, "executed"

    def _build_command(self, step: dict[str, Any]) -> JointState:
        settings = self.config.get("settings", {})
        arm_joints = list(
            settings.get("arm_joints", ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"])
        )
        gripper_joint = str(settings.get("gripper_joint", "joint7"))
        joint_names = arm_joints + [gripper_joint]
        current = self._latest_state_map()
        positions = {name: current.get(name, 0.0) for name in joint_names}

        pose_name = step.get("pose")
        if pose_name:
            pose = self.config.get("poses", {}).get(str(pose_name))
            if not isinstance(pose, dict):
                raise ValueError(f"unknown pose: {pose_name}")
            positions.update(self._positions_from_mapping(pose.get("positions", {})))

        positions.update(self._positions_from_mapping(step.get("positions", {})))

        if "gripper_width_m" in step:
            multiplier = float(settings.get("gripper_val_mutiple", 2.0)) or 1.0
            positions[gripper_joint] = float(step["gripper_width_m"]) / multiplier
        if "gripper_joint" in step:
            positions[gripper_joint] = float(step["gripper_joint"])

        speed = float(step.get("speed_percent", settings.get("default_speed_percent", 25.0)))
        speed = max(1.0, min(100.0, speed))
        effort = float(step.get("gripper_effort", settings.get("default_gripper_effort", 1.5)))

        command = JointState()
        command.header.frame_id = "piper_sequence_executor"
        command.name = joint_names
        command.position = [float(positions[name]) for name in joint_names]
        command.velocity = [speed if name in arm_joints else 0.0 for name in joint_names]
        command.effort = [effort if name == gripper_joint else 0.0 for name in joint_names]
        return command

    @staticmethod
    def _positions_from_mapping(value: Any) -> dict[str, float]:
        if not isinstance(value, dict):
            return {}
        return {str(name): float(position) for name, position in value.items()}

    def _wait_until_reached(self, command: JointState, timeout_sec: float) -> bool:
        deadline = time.monotonic() + max(timeout_sec, 0.0)
        while rclpy.ok() and time.monotonic() <= deadline:
            state_map = self._latest_state_map()
            if self._within_tolerance(command, state_map):
                return True
            command.header.stamp = self.get_clock().now().to_msg()
            self.command_pub.publish(command)
            time.sleep(0.1)
        return False

    def _within_tolerance(self, command: JointState, state_map: dict[str, float]) -> bool:
        for index, name in enumerate(command.name):
            if index >= len(command.position) or name not in state_map:
                return False
            tolerance = self.gripper_tolerance if name == "joint7" else self.position_tolerance
            if abs(float(command.position[index]) - state_map[name]) > tolerance:
                return False
        return True

    def _wait_for_state(self, timeout_sec: float) -> JointState | None:
        deadline = time.monotonic() + max(timeout_sec, 0.0)
        while rclpy.ok() and time.monotonic() <= deadline:
            with self.state_lock:
                if self.latest_state is not None:
                    return self.latest_state
            time.sleep(0.05)
        return None

    def _latest_state_map(self) -> dict[str, float]:
        with self.state_lock:
            state = self.latest_state
        if state is None:
            return {}
        return {
            name: float(state.position[index])
            for index, name in enumerate(state.name)
            if index < len(state.position)
        }

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            self.get_logger().warning(f"Config does not exist: {self.config_path}")
            return {}
        with self.config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        if not isinstance(data, dict):
            self.get_logger().warning(f"Config root must be a mapping: {self.config_path}")
            return {}
        data.setdefault("metadata", {})
        data.setdefault("settings", {})
        data.setdefault("poses", {})
        data.setdefault("sequences", {})
        return data


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PiperSequenceExecutor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
