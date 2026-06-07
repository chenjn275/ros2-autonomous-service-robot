#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WS_DIR="${REPO_ROOT}/ros2_ws"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  set +u
  # shellcheck source=/dev/null
  source /opt/ros/humble/setup.bash
  set -u
fi

HAS_PASSWORDLESS_SUDO=false
if sudo -n true 2>/dev/null; then
  HAS_PASSWORDLESS_SUDO=true
fi

if command -v rosdep >/dev/null 2>&1; then
  if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
    if [[ "${HAS_PASSWORDLESS_SUDO}" == "true" ]]; then
      sudo rosdep init || true
    else
      echo "未检测到免密 sudo，跳过 rosdep init。"
    fi
  fi
  rosdep update || true
  if [[ "${HAS_PASSWORDLESS_SUDO}" == "true" ]]; then
    rosdep install --from-paths "${WS_DIR}/src" --ignore-src -r -y --rosdistro humble || true
  else
    echo "未检测到免密 sudo，跳过 rosdep 自动安装；下面会打印 apt 安装命令。"
  fi
fi

if command -v apt-get >/dev/null 2>&1; then
  APT_PACKAGES=(
    can-utils \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-yaml \
    v4l-utils \
    ros-humble-ament-cmake \
    ros-humble-rclcpp \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-rviz2 \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-moveit \
    ros-humble-moveit-resources-panda-description \
    ros-humble-moveit-resources-panda-moveit-config \
    ros-humble-vision-msgs \
    ros-humble-std-srvs \
    ros-humble-rosbag2
  )
  OPTIONAL_APT_PACKAGES=(
    ros-humble-realsense2-camera
  )
  if [[ "${HAS_PASSWORDLESS_SUDO}" == "true" ]]; then
    sudo apt-get update
    sudo apt-get install -y "${APT_PACKAGES[@]}"
    AVAILABLE_OPTIONAL=()
    for pkg in "${OPTIONAL_APT_PACKAGES[@]}"; do
      if apt-cache show "${pkg}" >/dev/null 2>&1; then
        AVAILABLE_OPTIONAL+=("${pkg}")
      else
        echo "可选依赖未在当前 apt 源中找到，跳过：${pkg}"
      fi
    done
    if [[ "${#AVAILABLE_OPTIONAL[@]}" -gt 0 ]]; then
      sudo apt-get install -y "${AVAILABLE_OPTIONAL[@]}"
    fi
  else
    echo "未检测到免密 sudo。请手动安装缺失依赖："
    printf '  sudo apt-get install -y'
    printf ' %q' "${APT_PACKAGES[@]}"
    printf '\n'
    echo "可选硬件依赖可按需安装："
    printf '  sudo apt-get install -y'
    printf ' %q' "${OPTIONAL_APT_PACKAGES[@]}"
    printf '\n'
  fi
fi
