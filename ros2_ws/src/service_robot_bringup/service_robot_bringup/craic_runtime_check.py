import argparse
import time
from typing import Iterable

import rclpy
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState, LaserScan
from std_msgs.msg import String
from std_srvs.srv import Trigger


MESSAGE_TYPES = {
    "Image": Image,
    "JointState": JointState,
    "LaserScan": LaserScan,
    "String": String,
}


class RuntimeCheckNode(Node):
    def __init__(self) -> None:
        super().__init__("craic_runtime_check")


def wait_for_topic(node: RuntimeCheckNode, topic: str, msg_type_name: str, timeout_sec: float) -> bool:
    received = False
    msg_type = MESSAGE_TYPES[msg_type_name]

    def callback(_msg) -> None:
        nonlocal received
        received = True

    subscription = node.create_subscription(msg_type, topic, callback, 10)
    deadline = time.monotonic() + timeout_sec
    try:
        while rclpy.ok() and time.monotonic() <= deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            if received:
                return True
    finally:
        node.destroy_subscription(subscription)
    return False


def wait_for_service(node: RuntimeCheckNode, service_name: str, timeout_sec: float) -> bool:
    client = node.create_client(Trigger, service_name)
    try:
        return client.wait_for_service(timeout_sec=timeout_sec)
    finally:
        node.destroy_client(client)


def wait_for_nav2_action(node: RuntimeCheckNode, timeout_sec: float) -> bool:
    client = ActionClient(node, NavigateToPose, "navigate_to_pose")
    try:
        return client.wait_for_server(timeout_sec=timeout_sec)
    finally:
        client.destroy()


def parse_topic_spec(spec: str) -> tuple[str, str]:
    if ":" not in spec:
        raise ValueError(f"topic spec must be TOPIC:TYPE, got: {spec}")
    topic, msg_type_name = spec.rsplit(":", 1)
    if msg_type_name not in MESSAGE_TYPES:
        raise ValueError(
            f"unsupported message type {msg_type_name}; supported={sorted(MESSAGE_TYPES)}"
        )
    return topic, msg_type_name


def check_topics(node: RuntimeCheckNode, specs: Iterable[str], timeout_sec: float) -> list[str]:
    errors = []
    for spec in specs:
        topic, msg_type_name = parse_topic_spec(spec)
        print(f"waiting topic {topic} [{msg_type_name}] ...", flush=True)
        if not wait_for_topic(node, topic, msg_type_name, timeout_sec):
            errors.append(f"topic timeout: {topic} [{msg_type_name}]")
    return errors


def check_services(node: RuntimeCheckNode, names: Iterable[str], timeout_sec: float) -> list[str]:
    errors = []
    for service_name in names:
        print(f"waiting service {service_name} ...", flush=True)
        if not wait_for_service(node, service_name, timeout_sec):
            errors.append(f"service timeout: {service_name}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", action="append", default=[])
    parser.add_argument("--service", action="append", default=[])
    parser.add_argument("--nav2-action", action="store_true")
    parser.add_argument("--timeout-sec", type=float, default=20.0)
    args = parser.parse_args()

    rclpy.init()
    node = RuntimeCheckNode()
    try:
        errors = []
        errors += check_topics(node, args.topic, args.timeout_sec)
        errors += check_services(node, args.service, args.timeout_sec)
        if args.nav2_action:
            print("waiting action navigate_to_pose ...", flush=True)
            if not wait_for_nav2_action(node, args.timeout_sec):
                errors.append("action timeout: navigate_to_pose")
        if errors:
            print("RUNTIME CHECK FAILED")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)
        print("RUNTIME CHECK OK")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
