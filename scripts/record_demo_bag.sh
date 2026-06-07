#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BAG_DIR="${REPO_ROOT}/bags/service_robot_demo_$(date +%Y%m%d_%H%M%S)"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  set +u
  # shellcheck source=/dev/null
  source /opt/ros/humble/setup.bash
  set -u
fi

if [[ -f "${REPO_ROOT}/ros2_ws/install/setup.bash" ]]; then
  set +u
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/ros2_ws/install/setup.bash"
  set -u
fi

mkdir -p "$(dirname "${BAG_DIR}")"
echo "开始录制 rosbag：${BAG_DIR}"
ros2 bag record \
  -o "${BAG_DIR}" \
  /tf \
  /tf_static \
  /scan \
  /odom \
  /cmd_vel \
  /camera/image_raw \
  /perception/qr/result \
  /perception/yolo/detections
