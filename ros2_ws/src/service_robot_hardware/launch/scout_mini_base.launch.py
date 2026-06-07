from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration

from service_robot_hardware.optional_launch import include_optional_launch


def launch_setup(context, *args, **kwargs):
    return include_optional_launch(
        "scout_base",
        [
            "launch/scout_base.launch.py",
            "launch/scout_mini_base.launch.py",
            "scout_mini_base.launch.py",
            "scout_base.launch.py",
        ],
        {
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "port_name": LaunchConfiguration("port_name"),
            "odom_frame": LaunchConfiguration("odom_frame"),
            "base_frame": LaunchConfiguration("base_frame"),
            "odom_topic_name": LaunchConfiguration("odom_topic_name"),
            "is_scout_mini": LaunchConfiguration("is_scout_mini"),
            "is_omni_wheel": LaunchConfiguration("is_omni_wheel"),
            "simulated_robot": LaunchConfiguration("simulated_robot"),
            "control_rate": LaunchConfiguration("control_rate"),
        },
        "Fetch agilexrobotics/scout_ros2 and bring up CAN before launching.",
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("port_name", default_value="can0"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("base_frame", default_value="base_footprint"),
            DeclareLaunchArgument("odom_topic_name", default_value="odom"),
            DeclareLaunchArgument("is_scout_mini", default_value="true"),
            DeclareLaunchArgument("is_omni_wheel", default_value="false"),
            DeclareLaunchArgument("simulated_robot", default_value="false"),
            DeclareLaunchArgument("control_rate", default_value="50"),
            OpaqueFunction(function=launch_setup),
        ]
    )
