from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    timeout_sec = LaunchConfiguration("timeout_sec")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "timeout_sec",
                default_value="2.0",
                description="Seconds before a sensor topic is marked stale.",
            ),
            Node(
                package="service_robot_system",
                executable="system_health_node",
                name="system_health_node",
                output="screen",
                parameters=[{"timeout_sec": timeout_sec}],
            ),
        ]
    )
