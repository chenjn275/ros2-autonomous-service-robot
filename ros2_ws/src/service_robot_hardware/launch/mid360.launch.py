from launch import LaunchDescription
from launch.actions import OpaqueFunction

from service_robot_hardware.optional_launch import include_optional_launch


def launch_setup(context, *args, **kwargs):
    return include_optional_launch(
        "livox_ros_driver2",
        [
            "launch_ROS2/msg_MID360_launch.py",
            "launch/msg_MID360_launch.py",
            "msg_MID360_launch.py",
        ],
        {},
        "Fetch Livox-SDK/livox_ros_driver2 and configure host/lidar IP before launching.",
    )


def generate_launch_description():
    return LaunchDescription([OpaqueFunction(function=launch_setup)])
