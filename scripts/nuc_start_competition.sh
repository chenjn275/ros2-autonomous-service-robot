#!/usr/bin/env bash
set -euo pipefail

WS=${WS:-/home/chen/ros2-autonomous-service-robot/ros2_ws}
CONFIG=${CONFIG:-$WS/src/service_robot_bringup/config/craic2026_nuc.yaml}
SESSION=${SESSION:-craic_competition}

eval "$(
  python3 - "$CONFIG" <<'PY'
import shlex
import sys
import yaml

with open(sys.argv[1], encoding="utf-8") as stream:
    data = yaml.safe_load(stream) or {}


def get(path, default):
    value = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


fields = {
    "ROS_DOMAIN_ID_VALUE": get("ros_domain_id", 26),
    "ROS_LOCALHOST_ONLY_VALUE": get("ros_localhost_only", 1),
    "MAP_PATH": get("competition.map", ""),
    "NAV2_PARAMS": get("competition.nav2_params", ""),
    "MISSION_CONFIG": get("competition.mission_config", ""),
    "MARKER_CONFIG": get("competition.marker_config", ""),
    "PIPER_SEQUENCE_CONFIG": get("competition.piper_sequence_config", ""),
    "YOLO_MODEL_PATH": get("competition.yolo_model_path", ""),
    "CAMERA_NAME": get("hardware.camera_name", "d425i"),
    "CAMERA_SERIAL_NO": get("hardware.camera_serial_no", ""),
    "IMAGE_TOPIC": get("hardware.image_topic", "/d425i/color/image_raw"),
    "SCAN_TOPIC": get("hardware.scan_topic", "/scan"),
    "BASE_CAN_PORT": get("hardware.base_can_port", "can0"),
    "PIPER_CAN_PORT": get("hardware.piper_can_port", "can1"),
    "PIPER_AUTO_ENABLE": get("hardware.piper_auto_enable", True),
    "START_LIDAR": get("hardware.start_lidar", True),
    "YOLO_CONFIDENCE": get("perception.yolo_confidence", 0.45),
    "MARKER_MATCH_THRESHOLD": get("perception.marker_match_threshold", 0.65),
    "REQUIRE_PIPER_CALIBRATED": get("runtime.require_piper_calibrated", True),
    "PIPER_DRY_RUN": get("runtime.piper_dry_run", False),
    "PIPER_START_DRIVER": get("runtime.piper_start_driver", True),
    "MISSION_USE_NAV": get("runtime.mission_use_nav", True),
    "START_HARDWARE": get("runtime.start_hardware", True),
    "START_NAVIGATION": get("runtime.start_navigation", True),
    "START_PERCEPTION": get("runtime.start_perception", True),
    "START_MANIPULATION": get("runtime.start_manipulation", True),
    "START_MISSION": get("runtime.start_mission", True),
    "NAVIGATOR_READY_TIMEOUT_SEC": get("runtime.navigator_ready_timeout_sec", 60.0),
}

for name, value in fields.items():
    print(f"{name}={shlex.quote(value)}")
PY
)"

BASE_ENV="cd $WS && source /opt/ros/humble/setup.bash && source install/setup.bash && export ROS_DOMAIN_ID=$ROS_DOMAIN_ID_VALUE && export ROS_LOCALHOST_ONLY=$ROS_LOCALHOST_ONLY_VALUE"

cd "$WS"
set +u
source /opt/ros/humble/setup.bash
source install/setup.bash
set -u
export ROS_DOMAIN_ID="$ROS_DOMAIN_ID_VALUE"
export ROS_LOCALHOST_ONLY="$ROS_LOCALHOST_ONLY_VALUE"

if [ "${SKIP_PREFLIGHT:-0}" != "1" ]; then
  ros2 run service_robot_bringup craic_nuc_preflight -- --config "$CONFIG" --strict
else
  echo "WARNING: SKIP_PREFLIGHT=1; strict real-robot gate is bypassed."
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is required. Install it with: sudo apt install tmux" >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session already exists: $SESSION" >&2
  echo "Attach with: tmux attach -t $SESSION" >&2
  exit 1
fi

launch_cmd="$BASE_ENV; sleep 2; ros2 launch service_robot_bringup craic2026_competition.launch.py \
map:=$MAP_PATH \
nav2_params:=$NAV2_PARAMS \
mission_config:=$MISSION_CONFIG \
marker_config:=$MARKER_CONFIG \
piper_sequence_config:=$PIPER_SEQUENCE_CONFIG \
yolo_model_path:=$YOLO_MODEL_PATH \
camera_name:=$CAMERA_NAME \
camera_serial_no:=$CAMERA_SERIAL_NO \
image_topic:=$IMAGE_TOPIC \
base_can_port:=$BASE_CAN_PORT \
piper_can_port:=$PIPER_CAN_PORT \
piper_auto_enable:=$PIPER_AUTO_ENABLE \
start_lidar:=$START_LIDAR \
yolo_confidence:=$YOLO_CONFIDENCE \
marker_match_threshold:=$MARKER_MATCH_THRESHOLD \
require_piper_calibrated:=$REQUIRE_PIPER_CALIBRATED \
piper_dry_run:=$PIPER_DRY_RUN \
piper_start_driver:=$PIPER_START_DRIVER \
mission_use_nav:=$MISSION_USE_NAV \
start_hardware:=$START_HARDWARE \
start_navigation:=$START_NAVIGATION \
start_perception:=$START_PERCEPTION \
start_manipulation:=$START_MANIPULATION \
start_mission:=$START_MISSION \
navigator_ready_timeout_sec:=$NAVIGATOR_READY_TIMEOUT_SEC; exec bash"

runtime_check_cmd="$BASE_ENV; sleep 12; ros2 run service_robot_bringup craic_runtime_check -- \
--topic $IMAGE_TOPIC:Image \
--topic /perception/yolo/detections:String \
--topic /perception/custom_marker/result:String \
--topic /joint_states_feedback:JointState \
--topic $SCAN_TOPIC:LaserScan \
--service /manipulation/piper/pick \
--service /manipulation/piper/place_001 \
--service /manipulation/piper/place_002 \
--service /manipulation/piper/place_003 \
--service /manipulation/piper/place_004 \
--nav2-action \
--timeout-sec 45.0; exec bash"

tmux new-session -d -s "$SESSION" -n preflight \
  "$BASE_ENV; ros2 run service_robot_bringup craic_nuc_preflight -- --config $CONFIG --strict; exec bash"
tmux new-window -t "$SESSION" -n competition "$launch_cmd"
tmux new-window -t "$SESSION" -n runtime-check "$runtime_check_cmd"

echo "Started tmux session: $SESSION"
echo "Attach: tmux attach -t $SESSION"
echo "Stop: scripts/nuc_stop_competition.sh"
