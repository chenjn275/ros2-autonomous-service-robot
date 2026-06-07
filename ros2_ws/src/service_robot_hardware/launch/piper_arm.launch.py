from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration

from service_robot_hardware.optional_launch import include_optional_launch


def launch_setup(context, *args, **kwargs):
    return include_optional_launch(
        "piper",
        [
            "launch/start_single_piper.launch",
            "launch/start_single_piper.launch.py",
            "launch/piper_single.launch",
            "launch/piper_single.launch.py",
        ],
        {
            "port_name": LaunchConfiguration("port_name"),
            "auto_enable": LaunchConfiguration("auto_enable"),
        },
        "Fetch the ROS2-compatible Piper driver branch and bring up the arm CAN interface before launching.",
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("port_name", default_value="can1"),
            DeclareLaunchArgument("auto_enable", default_value="false"),
            OpaqueFunction(function=launch_setup),
        ]
    )
