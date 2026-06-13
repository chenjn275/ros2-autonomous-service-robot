#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 POSE_NAME [--calibrated]" >&2
  exit 2
fi

POSE_NAME=$1
MARK_CALIBRATED=false
if [ "${2:-}" = "--calibrated" ]; then
  MARK_CALIBRATED=true
fi

WS=${WS:-/home/chen/ros2-autonomous-service-robot/ros2_ws}
CONFIG=${CONFIG:-$WS/src/service_robot_manipulation/config/piper_pick_place_sequences.yaml}

cd "$WS"
set +u
source /opt/ros/humble/setup.bash
source install/setup.bash
set -u

ros2 run service_robot_manipulation piper_pose_recorder --ros-args \
  -p pose_name:="$POSE_NAME" \
  -p config_path:="$CONFIG" \
  -p mark_calibrated:="$MARK_CALIBRATED"
