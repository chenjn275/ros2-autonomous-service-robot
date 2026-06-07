#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EXTERNAL_SRC="${REPO_ROOT}/external_ws/src"

mkdir -p "${EXTERNAL_SRC}"

clone_or_update() {
  local name="$1"
  local url="$2"
  local branch="${3:-}"
  local target="${EXTERNAL_SRC}/${name}"

  if [[ -d "${target}/.git" ]]; then
    echo "更新：${name}"
    git -C "${target}" fetch --all --prune
    if [[ -n "${branch}" ]]; then
      git -C "${target}" checkout "${branch}"
      git -C "${target}" pull --ff-only origin "${branch}" || true
    else
      git -C "${target}" pull --ff-only || true
    fi
    return
  fi

  echo "拉取：${name}"
  if [[ -n "${branch}" ]]; then
    if ! git clone --depth 1 --branch "${branch}" "${url}" "${target}"; then
      rm -rf "${target}"
      return 1
    fi
  else
    if ! git clone --depth 1 "${url}" "${target}"; then
      rm -rf "${target}"
      return 1
    fi
  fi
}

clone_or_update realsense-ros https://github.com/IntelRealSense/realsense-ros.git ros2-master || \
  clone_or_update realsense-ros https://github.com/IntelRealSense/realsense-ros.git
clone_or_update livox_ros_driver2 https://github.com/Livox-SDK/livox_ros_driver2.git
clone_or_update scout_ros2 https://github.com/agilexrobotics/scout_ros2.git humble

PIPER_BRANCHES=()
if [[ -n "${PIPER_BRANCH:-}" ]]; then
  PIPER_BRANCHES+=("${PIPER_BRANCH}")
fi
PIPER_BRANCHES+=("ros-foxy-no-aloha" "humble" "main")

for branch in "${PIPER_BRANCHES[@]}"; do
  if clone_or_update piper_ros https://github.com/agilexrobotics/piper_ros.git "${branch}"; then
    break
  fi
done

echo "完成。外部驱动位于：${EXTERNAL_SRC}"
echo "external_ws/ 已写入 .gitignore，不会提交外部仓库历史。"
