#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${REPO_ROOT}/assets/demo_runs/nav_task"
LOG_DIR="${RUN_DIR}/logs"
BAG_DIR="${RUN_DIR}/rosbag_nav_task"

rm -rf "${RUN_DIR}"
mkdir -p "${LOG_DIR}"

pkill -9 gzserver 2>/dev/null || true
pkill -9 gzclient 2>/dev/null || true
pkill -x map_server 2>/dev/null || true
pkill -x amcl 2>/dev/null || true
pkill -x controller_server 2>/dev/null || true
pkill -x smoother_server 2>/dev/null || true
pkill -x planner_server 2>/dev/null || true
pkill -x behavior_server 2>/dev/null || true
pkill -x bt_navigator 2>/dev/null || true
pkill -x lifecycle_manager 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
sleep 2

set +u
# shellcheck source=/dev/null
source /opt/ros/humble/setup.bash
# shellcheck source=/dev/null
source "${REPO_ROOT}/ros2_ws/install/setup.bash"
set -u

ros2 daemon stop >/dev/null 2>&1 || true

setsid ros2 launch service_robot_simulation gazebo.launch.py \
  gui:=false \
  > "${LOG_DIR}/gazebo.launch.log" 2>&1 &
GAZEBO_PID=$!
NAV_PID=0
TASK_PID=0
QR_PID=0
YOLO_PID=0
SYSTEM_PID=0
BAG_PID=0

stop_process_groups() {
  for pid in "$@"; do
    if [ -n "${pid}" ] && [ "${pid}" -gt 0 ] 2>/dev/null; then
      kill -TERM "-${pid}" 2>/dev/null || true
      kill "${pid}" 2>/dev/null || true
    fi
  done
  sleep 2
  for pid in "$@"; do
    if [ -n "${pid}" ] && [ "${pid}" -gt 0 ] 2>/dev/null; then
      kill -KILL "-${pid}" 2>/dev/null || true
      kill -KILL "${pid}" 2>/dev/null || true
    fi
  done
}

cleanup() {
  if [ -n "${BAG_PID:-}" ] && [ "${BAG_PID}" -gt 0 ] 2>/dev/null; then
    kill -INT "-${BAG_PID}" 2>/dev/null || true
    kill -INT "${BAG_PID}" 2>/dev/null || true
    wait "${BAG_PID}" 2>/dev/null || true
  fi
  stop_process_groups "${TASK_PID:-0}" "${SYSTEM_PID:-0}" "${YOLO_PID:-0}" "${QR_PID:-0}" \
    "${NAV_PID:-0}" "${GAZEBO_PID:-0}"
}
trap cleanup EXIT

ODOM_READY=0
for _ in {1..180}; do
  if grep -F "Advertise odometry on [/odom]" "${LOG_DIR}/gazebo.launch.log" >/dev/null 2>&1; then
    ODOM_READY=1
    break
  fi
  sleep 1
done

if [ "${ODOM_READY}" -ne 1 ]; then
  echo "ERROR: Gazebo diff-drive odometry was not advertised before Nav2 startup." \
    > "${LOG_DIR}/gazebo_odom_wait.log"
  exit 1
else
  echo "OK: Gazebo diff-drive odometry advertised." \
    > "${LOG_DIR}/gazebo_odom_wait.log"
fi

setsid ros2 launch service_robot_navigation navigation.launch.py \
  use_sim_time:=true \
  > "${LOG_DIR}/navigation.launch.log" 2>&1 &
NAV_PID=$!

NAV_READY=0
for _ in {1..240}; do
  if grep -F "lifecycle_manager_navigation" "${LOG_DIR}/navigation.launch.log" \
      | grep -F "Managed nodes are active" >/dev/null 2>&1; then
    NAV_READY=1
    break
  fi
  sleep 1
done

if [ "${NAV_READY}" -ne 1 ]; then
  echo "ERROR: Nav2 lifecycle manager did not report active." \
    > "${LOG_DIR}/nav_ready.log"
else
  echo "OK: Nav2 lifecycle manager reported active." \
    > "${LOG_DIR}/nav_ready.log"
fi

sleep 5

timeout 15s ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}" \
  > "${LOG_DIR}/initialpose.log" 2>&1 || true

setsid ros2 launch service_robot_perception qr_detection.launch.py \
  use_sim_time:=true \
  > "${LOG_DIR}/qr_detection.launch.log" 2>&1 &
QR_PID=$!

setsid ros2 launch service_robot_perception yolo_detection.launch.py \
  use_sim_time:=true \
  > "${LOG_DIR}/yolo_detection.launch.log" 2>&1 &
YOLO_PID=$!

setsid ros2 launch service_robot_system system_health.launch.py \
  > "${LOG_DIR}/system_health.launch.log" 2>&1 &
SYSTEM_PID=$!

setsid ros2 bag record \
  --include-unpublished-topics \
  --polling-interval 500 \
  -o "${BAG_DIR}" \
  /tf /tf_static /map /odom /scan /cmd_vel /camera/image_raw \
  /livox/lidar /livox/imu /tasks/status /system/health \
  > "${LOG_DIR}/rosbag_record.log" 2>&1 &
BAG_PID=$!

sleep 5

setsid ros2 launch service_robot_tasks task_commander.launch.py \
  use_nav:=true \
  use_sim_time:=false \
  start_delay_sec:=1.0 \
  nav_server_wait_sec:=120.0 \
  nav_goal_send_timeout_sec:=45.0 \
  default_nav_timeout_sec:=60.0 \
  > "${LOG_DIR}/task_commander_nav.log" 2>&1 &
TASK_PID=$!

sleep 160

timeout 10s ros2 topic list | sort > "${RUN_DIR}/topic_list.txt" || true
timeout 10s ros2 node list | sort > "${RUN_DIR}/node_list.txt" || true
timeout 10s ros2 topic info /cmd_vel > "${RUN_DIR}/cmd_vel_info.txt" 2>&1 || true
timeout 10s ros2 topic echo --once /tasks/status > "${RUN_DIR}/tasks_status_once.txt" 2>&1 || true

kill -INT "${BAG_PID}" 2>/dev/null || true
wait "${BAG_PID}" 2>/dev/null || true
BAG_PID=""

echo "Nav task demo evidence saved to ${RUN_DIR}"
