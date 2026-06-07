from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include_hardware(launch_file, condition):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("service_robot_hardware"), "launch", launch_file]
            )
        ),
        condition=IfCondition(condition),
    )


def generate_launch_description():
    start_camera = LaunchConfiguration("start_camera")
    start_base = LaunchConfiguration("start_base")
    start_lidar = LaunchConfiguration("start_lidar")
    start_arm = LaunchConfiguration("start_arm")
    start_nuc_profile = LaunchConfiguration("start_nuc_profile")

    return LaunchDescription(
        [
            DeclareLaunchArgument("start_camera", default_value="true"),
            DeclareLaunchArgument("start_base", default_value="true"),
            DeclareLaunchArgument("start_lidar", default_value="true"),
            DeclareLaunchArgument("start_arm", default_value="false"),
            DeclareLaunchArgument("start_nuc_profile", default_value="true"),
            include_hardware("nuc_ultra_profile.launch.py", start_nuc_profile),
            include_hardware("realsense_d425i.launch.py", start_camera),
            include_hardware("scout_mini_base.launch.py", start_base),
            include_hardware("mid360.launch.py", start_lidar),
            include_hardware("piper_arm.launch.py", start_arm),
        ]
    )
