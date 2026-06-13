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
            "can_port": LaunchConfiguration("can_port"),
            "auto_enable": LaunchConfiguration("auto_enable"),
            "gripper_exist": LaunchConfiguration("gripper_exist"),
            "gripper_val_mutiple": LaunchConfiguration("gripper_val_mutiple"),
            "command_topic": LaunchConfiguration("command_topic"),
        },
        "Fetch the ROS2-compatible Piper driver branch and bring up the arm CAN interface before launching.",
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("can_port", default_value="can1"),
            DeclareLaunchArgument("auto_enable", default_value="false"),
            DeclareLaunchArgument("gripper_exist", default_value="true"),
            DeclareLaunchArgument("gripper_val_mutiple", default_value="2"),
            DeclareLaunchArgument("command_topic", default_value="/joint_command"),
            OpaqueFunction(function=launch_setup),
        ]
    )
