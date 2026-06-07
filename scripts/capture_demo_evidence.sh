#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${REPO_ROOT}/assets/demo_runs/latest"
LOG_DIR="${RUN_DIR}/logs"
BAG_DIR="${RUN_DIR}/rosbag_nav_task"

rm -rf "${RUN_DIR}"
mkdir -p "${LOG_DIR}"

pkill -f gzserver 2>/dev/null || true
pkill -f gzclient 2>/dev/null || true
pkill -f robot_state_publisher 2>/dev/null || true
pkill -f spawn_entity.py 2>/dev/null || true
sleep 2

set +u
# shellcheck source=/dev/null
source /opt/ros/humble/setup.bash
# shellcheck source=/dev/null
source "${REPO_ROOT}/ros2_ws/install/setup.bash"
set -u

wait_for_topic() {
  local topic="$1"
  local timeout_sec="$2"
  local start
  start="$(date +%s)"
  while true; do
    if ros2 topic list 2>/dev/null | awk -v wanted="${topic}" '$0 == wanted {found=1} END {exit(found ? 0 : 1)}'; then
      return 0
    fi
    if (( "$(date +%s)" - start >= timeout_sec )); then
      echo "等待话题超时：${topic}" | tee -a "${LOG_DIR}/capture.log"
      return 1
    fi
    sleep 2
  done
}

ros2 launch service_robot_bringup demo.launch.py \
  gui:=false \
  start_navigation:=false \
  start_perception:=true \
  start_tasks:=true \
  start_system:=true \
  > "${LOG_DIR}/demo.launch.log" 2>&1 &
DEMO_PID=$!
BAG_PID=""

cleanup() {
  if [[ -n "${BAG_PID}" ]]; then
    kill -INT "${BAG_PID}" 2>/dev/null || true
  fi
  kill "${DEMO_PID}" 2>/dev/null || true
}
trap cleanup EXIT

ros2 bag record \
  --include-unpublished-topics \
  --polling-interval 500 \
  -o "${BAG_DIR}" \
  /tf \
  /tf_static \
  /odom \
  /scan \
  /cmd_vel \
  /camera/image_raw \
  /livox/lidar \
  /livox/imu \
  /tasks/status \
  /system/health \
  > "${LOG_DIR}/rosbag_record.log" 2>&1 &
BAG_PID=$!

wait_for_topic /scan 120 || true
wait_for_topic /camera/image_raw 120 || true
wait_for_topic /livox/lidar 120 || true
wait_for_topic /livox/imu 120 || true
wait_for_topic /tasks/status 60 || true
wait_for_topic /system/health 60 || true

ros2 topic list | sort > "${RUN_DIR}/topic_list.txt" || true
ros2 node list | sort > "${RUN_DIR}/node_list.txt" || true

python3 "${SCRIPT_DIR}/save_image_once.py" \
  --topic /camera/image_raw \
  --output "${RUN_DIR}/demo_camera_frame.png" \
  --timeout 20 || true

sleep 40
kill -INT "${BAG_PID}" 2>/dev/null || true
wait "${BAG_PID}" 2>/dev/null || true
BAG_PID=""

ros2 topic info /scan > "${RUN_DIR}/scan_info.txt" 2>&1 || true
ros2 topic info /odom > "${RUN_DIR}/odom_info.txt" 2>&1 || true
ros2 topic info /camera/image_raw > "${RUN_DIR}/camera_info.txt" 2>&1 || true
ros2 topic info /livox/lidar > "${RUN_DIR}/livox_lidar_info.txt" 2>&1 || true
ros2 topic info /livox/imu > "${RUN_DIR}/livox_imu_info.txt" 2>&1 || true

echo "Demo evidence saved to ${RUN_DIR}"
