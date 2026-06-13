from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    command_topic = LaunchConfiguration("command_topic")
    config_path = LaunchConfiguration("config_path")

    return LaunchDescription(
        [
            DeclareLaunchArgument("start_driver", default_value="true"),
            DeclareLaunchArgument("can_port", default_value="can0"),
            DeclareLaunchArgument("auto_enable", default_value="true"),
            DeclareLaunchArgument("gripper_exist", default_value="true"),
            DeclareLaunchArgument("gripper_val_mutiple", default_value="2"),
            DeclareLaunchArgument("log_level", default_value="warn"),
            DeclareLaunchArgument("command_topic", default_value="/joint_command"),
            DeclareLaunchArgument(
                "config_path",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_manipulation/config/piper_pick_place_sequences.yaml"
                ),
            ),
            DeclareLaunchArgument("require_calibrated", default_value="true"),
            DeclareLaunchArgument("dry_run", default_value="false"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("piper"), "launch", "start_single_piper.launch.py"]
                    )
                ),
                launch_arguments={
                    "can_port": LaunchConfiguration("can_port"),
                    "auto_enable": LaunchConfiguration("auto_enable"),
                    "gripper_exist": LaunchConfiguration("gripper_exist"),
                    "gripper_val_mutiple": LaunchConfiguration("gripper_val_mutiple"),
                    "command_topic": command_topic,
                    "log_level": LaunchConfiguration("log_level"),
                    "can_loss_grace_sec": "1.5",
                }.items(),
                condition=IfCondition(LaunchConfiguration("start_driver")),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("service_robot_manipulation"),
                            "launch",
                            "piper_fixed_sequences.launch.py",
                        ]
                    )
                ),
                launch_arguments={
                    "config_path": config_path,
                    "command_topic": command_topic,
                    "require_calibrated": LaunchConfiguration("require_calibrated"),
                    "dry_run": LaunchConfiguration("dry_run"),
                }.items(),
            ),
        ]
    )
