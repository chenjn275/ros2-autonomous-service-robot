#!/usr/bin/env bash
set -euo pipefail

WS=${WS:-/home/chen/ros2-autonomous-service-robot/ros2_ws}
VENVNV_REPO=${VENVNV_REPO:-https://github.com/Alex10086/Venom_VNV.git}
VENVNV_BRANCH=${VENVNV_BRANCH:-feat/yolo_detect_digit}
VENVNV_DIR=${VENVNV_DIR:-$WS/src/Venom_VNV}
SKIP_PACKAGES=(
  piper_gazebo
  piper_mujoco
  piper_with_gripper_moveit
  piper_no_gripper_moveit
)

cd "$WS"

if [ ! -d "$VENVNV_DIR/.git" ]; then
  if [ -e "$VENVNV_DIR" ]; then
    echo "ERROR: $VENVNV_DIR exists but is not a git repository." >&2
    echo "Move it away or clone $VENVNV_REPO branch $VENVNV_BRANCH there manually." >&2
    exit 1
  fi
  git clone --depth 1 --branch "$VENVNV_BRANCH" --single-branch "$VENVNV_REPO" "$VENVNV_DIR"
else
  current_branch=$(git -C "$VENVNV_DIR" branch --show-current || true)
  if [ "$current_branch" != "$VENVNV_BRANCH" ]; then
    echo "WARNING: $VENVNV_DIR is on branch '$current_branch', expected '$VENVNV_BRANCH'." >&2
  fi
fi

set +u
source /opt/ros/humble/setup.bash
set -u

colcon build --symlink-install --packages-skip "${SKIP_PACKAGES[@]}"

echo "Build complete. Run: source $WS/install/setup.bash"
