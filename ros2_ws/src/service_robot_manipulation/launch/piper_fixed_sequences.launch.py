from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_path",
                default_value=(
                    "/home/chen/ros2-autonomous-service-robot/ros2_ws/src/"
                    "service_robot_manipulation/config/piper_pick_place_sequences.yaml"
                ),
            ),
            DeclareLaunchArgument("command_topic", default_value="/joint_command"),
            DeclareLaunchArgument("state_topic", default_value="/joint_states_feedback"),
            DeclareLaunchArgument("service_prefix", default_value="/manipulation/piper"),
            DeclareLaunchArgument("require_calibrated", default_value="true"),
            DeclareLaunchArgument("dry_run", default_value="false"),
            Node(
                package="service_robot_manipulation",
                executable="piper_sequence_executor",
                name="piper_sequence_executor",
                output="screen",
                parameters=[
                    {
                        "config_path": LaunchConfiguration("config_path"),
                        "command_topic": LaunchConfiguration("command_topic"),
                        "state_topic": LaunchConfiguration("state_topic"),
                        "service_prefix": LaunchConfiguration("service_prefix"),
                        "require_calibrated": ParameterValue(
                            LaunchConfiguration("require_calibrated"), value_type=bool
                        ),
                        "dry_run": ParameterValue(
                            LaunchConfiguration("dry_run"), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
