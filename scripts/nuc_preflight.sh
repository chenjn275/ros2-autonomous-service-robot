#!/usr/bin/env bash
set -euo pipefail

WS=${WS:-/home/chen/ros2-autonomous-service-robot/ros2_ws}
CONFIG=${CONFIG:-$WS/src/service_robot_bringup/config/craic2026_nuc.yaml}

cd "$WS"
set +u
source /opt/ros/humble/setup.bash
source install/setup.bash
set -u

ros2 run service_robot_bringup craic_nuc_preflight -- --config "$CONFIG" --strict
