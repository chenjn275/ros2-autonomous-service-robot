import argparse
from pathlib import Path
from typing import Any

import yaml

from service_robot_manipulation.piper_sequence_executor import default_config_path


REQUIRED_SEQUENCES = ["pick", "place_001", "place_002", "place_003", "place_004"]


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError("config root must be a mapping")
    return data


def referenced_poses(sequence: list[Any]) -> list[str]:
    names = []
    for step in sequence:
        if isinstance(step, dict) and step.get("pose"):
            names.append(str(step["pose"]))
    return names


def validate_config(config: dict[str, Any], strict: bool) -> list[str]:
    errors = []
    metadata = config.get("metadata", {})
    poses = config.get("poses", {})
    sequences = config.get("sequences", {})

    if strict and not bool(metadata.get("calibrated", False)):
        errors.append("metadata.calibrated must be true for strict real-robot execution")

    for sequence_name in REQUIRED_SEQUENCES:
        sequence = sequences.get(sequence_name)
        if not isinstance(sequence, list) or not sequence:
            errors.append(f"missing or empty required sequence: {sequence_name}")
            continue
        for pose_name in referenced_poses(sequence):
            pose = poses.get(pose_name)
            if not isinstance(pose, dict):
                errors.append(f"sequence {sequence_name} references missing pose: {pose_name}")
                continue
            positions = pose.get("positions")
            if not isinstance(positions, dict) or not positions:
                errors.append(f"pose {pose_name} has no positions")
            if strict and bool(pose.get("placeholder", False)):
                errors.append(f"pose {pose_name} is still marked placeholder")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=default_config_path())
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require calibrated metadata and reject placeholder poses.",
    )
    args = parser.parse_args()

    path = Path(args.config).expanduser()
    config = load_config(path)
    errors = validate_config(config, args.strict)
    if errors:
        print(f"INVALID: {path}")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"OK: {path}")
    print("required sequences:", ", ".join(REQUIRED_SEQUENCES))


if __name__ == "__main__":
    main()
