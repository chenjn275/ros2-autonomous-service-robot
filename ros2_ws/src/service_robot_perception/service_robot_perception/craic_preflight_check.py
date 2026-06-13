from pathlib import Path
from typing import Any

from ament_index_python.packages import get_package_share_directory
import yaml


REQUIRED_MARKER_IDS = ["001", "002", "003", "004"]


def default_marker_config() -> Path:
    source_config = (
        Path.home()
        / "ros2-autonomous-service-robot"
        / "ros2_ws"
        / "src"
        / "service_robot_perception"
        / "config"
        / "custom_markers.yaml"
    )
    if source_config.exists():
        return source_config
    return Path(get_package_share_directory("service_robot_perception")) / "config" / "custom_markers.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def check_marker_templates(path: Path, strict: bool) -> list[str]:
    errors = []
    config = load_yaml(path)
    markers = {
        str(item.get("id", "")): item
        for item in config.get("markers", [])
        if isinstance(item, dict)
    }
    for marker_id in REQUIRED_MARKER_IDS:
        marker = markers.get(marker_id)
        if marker is None:
            errors.append(f"missing marker id: {marker_id}")
            continue
        template_path = str(marker.get("template_path", "")).strip()
        if strict and not template_path:
            errors.append(f"marker {marker_id} has no template_path")
            continue
        if template_path:
            resolved = Path(template_path)
            if not resolved.is_absolute():
                resolved = path.parent / resolved
            if not resolved.is_file():
                errors.append(f"marker {marker_id} template does not exist: {resolved}")
    return errors


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--marker-config", default=str(default_marker_config()))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    marker_config = Path(args.marker_config).expanduser()
    errors = check_marker_templates(marker_config, args.strict)
    if errors:
        print(f"INVALID marker config: {marker_config}")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"OK marker config: {marker_config}")


if __name__ == "__main__":
    main()
