import argparse
from pathlib import Path
from typing import Any

from service_robot_manipulation.piper_sequence_validator import (
    load_config as load_piper_config,
    validate_config as validate_piper_config,
)
from service_robot_perception.craic_preflight_check import check_marker_templates
from venom_mission_commander.craic_real_config_check import check_nav_placeholders
import yaml


DEFAULT_CONFIG = (
    Path.home()
    / "ros2-autonomous-service-robot"
    / "ros2_ws"
    / "src"
    / "service_robot_bringup"
    / "config"
    / "craic2026_nuc.yaml"
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def nested(config: dict[str, Any], *keys: str, default: str = "") -> str:
    value: Any = config
    for key in keys:
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    return str(value if value is not None else default)


def check_required_file(label: str, path_text: str) -> list[str]:
    path = Path(path_text).expanduser()
    if not path.is_file():
        return [f"{label} does not exist: {path}"]
    return []


def check_required_dir(label: str, path_text: str) -> list[str]:
    path = Path(path_text).expanduser()
    if not path.is_dir():
        return [f"{label} does not exist: {path}"]
    return []


def check_nuc_config(config_path: Path, strict: bool) -> list[str]:
    config = load_yaml(config_path)
    errors: list[str] = []

    workspace = nested(config, "workspace")
    mission_config = nested(config, "competition", "mission_config")
    marker_config = nested(config, "competition", "marker_config")
    piper_sequence_config = nested(config, "competition", "piper_sequence_config")
    yolo_model_path = nested(config, "competition", "yolo_model_path")
    map_path = nested(config, "competition", "map")
    nav2_params = nested(config, "competition", "nav2_params")

    errors += check_required_dir("workspace", workspace)
    errors += check_required_file("mission_config", mission_config)
    errors += check_required_file("marker_config", marker_config)
    errors += check_required_file("piper_sequence_config", piper_sequence_config)
    errors += check_required_file("yolo_model_path", yolo_model_path)
    errors += check_required_file("map", map_path)
    errors += check_required_file("nav2_params", nav2_params)

    image_topic = nested(config, "hardware", "image_topic")
    if not image_topic.startswith("/"):
        errors.append(f"hardware.image_topic must be absolute ROS topic: {image_topic}")

    base_can_port = nested(config, "hardware", "base_can_port")
    piper_can_port = nested(config, "hardware", "piper_can_port")
    if not base_can_port:
        errors.append("hardware.base_can_port is empty")
    if not piper_can_port:
        errors.append("hardware.piper_can_port is empty")
    if base_can_port and piper_can_port and base_can_port == piper_can_port:
        errors.append(
            "base_can_port and piper_can_port are identical. This is allowed only if "
            "your chassis and Piper are truly on the same CAN interface; otherwise set "
            "can0/can1 separately."
        )

    if Path(marker_config).expanduser().is_file():
        errors += check_marker_templates(Path(marker_config).expanduser(), strict)
    if Path(mission_config).expanduser().is_file():
        errors += check_nav_placeholders(Path(mission_config).expanduser(), strict)
    if Path(piper_sequence_config).expanduser().is_file():
        errors += validate_piper_config(
            load_piper_config(Path(piper_sequence_config).expanduser()), strict
        )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()
    errors = check_nuc_config(config_path, args.strict)
    if errors:
        print(f"INVALID NUC competition config: {config_path}")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"OK NUC competition config: {config_path}")


if __name__ == "__main__":
    main()
