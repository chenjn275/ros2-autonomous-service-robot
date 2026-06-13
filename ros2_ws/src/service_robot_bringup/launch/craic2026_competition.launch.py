from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include_launch(package_name, launch_file, arguments, condition):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare(package_name), "launch", launch_file])
        ),
        launch_arguments=arguments.items(),
        condition=IfCondition(condition),
    )


def generate_launch_description():
    start_hardware = LaunchConfiguration("start_hardware")
    start_navigation = LaunchConfiguration("start_navigation")
    start_perception = LaunchConfiguration("start_perception")
    start_manipulation = LaunchConfiguration("start_manipulation")
    start_mission = LaunchConfiguration("start_mission")

    use_sim_time = LaunchConfiguration("use_sim_time")
    image_topic = LaunchConfiguration("image_topic")
    yolo_model_path = LaunchConfiguration("yolo_model_path")
    yolo_confidence = LaunchConfiguration("yolo_confidence")
    marker_config = LaunchConfiguration("marker_config")
    marker_match_threshold = LaunchConfiguration("marker_match_threshold")

    return LaunchDescription(
        [
            DeclareLaunchArgument("start_hardware", default_value="true"),
            DeclareLaunchArgument("start_navigation", default_value="true"),
            DeclareLaunchArgument("start_perception", default_value="true"),
            DeclareLaunchArgument("start_manipulation", default_value="true"),
            DeclareLaunchArgument("start_mission", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("camera_name", default_value="d425i"),
            DeclareLaunchArgument("camera_serial_no", default_value=""),
            DeclareLaunchArgument("image_topic", default_value="/d425i/color/image_raw"),
            DeclareLaunchArgument("base_can_port", default_value="can0"),
            DeclareLaunchArgument("piper_can_port", default_value="can1"),
            DeclareLaunchArgument("piper_auto_enable", default_value="true"),
            DeclareLaunchArgument("start_lidar", default_value="true"),
            DeclareLaunchArgument(
                "map",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_navigation/maps/demo_map.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "nav2_params",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_navigation/config/nav2_params.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "mission_config",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "Venom_VNV/venom_mission_commander/config/craic2026_home_sorting_real.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "marker_config",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_perception/config/custom_markers.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "piper_sequence_config",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_manipulation/config/piper_pick_place_sequences.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "yolo_model_path",
                default_value="/home/chen/model_backup/craic_items_baseline_best.pt",
            ),
            DeclareLaunchArgument("yolo_confidence", default_value="0.45"),
            DeclareLaunchArgument("marker_match_threshold", default_value="0.65"),
            DeclareLaunchArgument("require_piper_calibrated", default_value="true"),
            DeclareLaunchArgument("piper_dry_run", default_value="false"),
            DeclareLaunchArgument("piper_start_driver", default_value="true"),
            DeclareLaunchArgument("mission_use_nav", default_value="true"),
            DeclareLaunchArgument("navigator_ready_timeout_sec", default_value="60.0"),
            include_launch(
                "service_robot_hardware",
                "hardware_bringup.launch.py",
                {
                    "start_camera": "true",
                    "start_base": "true",
                    "start_lidar": LaunchConfiguration("start_lidar"),
                    "start_arm": "false",
                    "start_nuc_profile": "true",
                    "camera_name": LaunchConfiguration("camera_name"),
                    "camera_serial_no": LaunchConfiguration("camera_serial_no"),
                    "base_can_port": LaunchConfiguration("base_can_port"),
                },
                start_hardware,
            ),
            include_launch(
                "service_robot_navigation",
                "navigation.launch.py",
                {
                    "map": LaunchConfiguration("map"),
                    "params_file": LaunchConfiguration("nav2_params"),
                    "use_sim_time": use_sim_time,
                    "autostart": "true",
                    "log_level": "info",
                },
                start_navigation,
            ),
            include_launch(
                "service_robot_perception",
                "craic2026_perception.launch.py",
                {
                    "image_topic": image_topic,
                    "yolo_model_path": yolo_model_path,
                    "yolo_confidence": yolo_confidence,
                    "marker_templates_config": marker_config,
                    "marker_match_threshold": marker_match_threshold,
                    "use_sim_time": use_sim_time,
                },
                start_perception,
            ),
            include_launch(
                "service_robot_manipulation",
                "piper_real_manipulation.launch.py",
                {
                    "start_driver": LaunchConfiguration("piper_start_driver"),
                    "can_port": LaunchConfiguration("piper_can_port"),
                    "auto_enable": LaunchConfiguration("piper_auto_enable"),
                    "config_path": LaunchConfiguration("piper_sequence_config"),
                    "require_calibrated": LaunchConfiguration("require_piper_calibrated"),
                    "dry_run": LaunchConfiguration("piper_dry_run"),
                    "command_topic": "/joint_command",
                },
                start_manipulation,
            ),
            include_launch(
                "venom_mission_commander",
                "mission_commander.launch.py",
                {
                    "mission_config": LaunchConfiguration("mission_config"),
                    "use_nav": LaunchConfiguration("mission_use_nav"),
                    "nav2_wait_mode": "bt_navigator",
                    "navigator_ready_timeout_sec": LaunchConfiguration(
                        "navigator_ready_timeout_sec"
                    ),
                    "use_sim_time": use_sim_time,
                },
                start_mission,
            ),
        ]
    )
