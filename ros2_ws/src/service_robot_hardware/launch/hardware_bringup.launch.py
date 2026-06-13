from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include_hardware(launch_file, condition, launch_arguments=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("service_robot_hardware"), "launch", launch_file]
            )
        ),
        launch_arguments=(launch_arguments or {}).items(),
        condition=IfCondition(condition),
    )


def generate_launch_description():
    start_camera = LaunchConfiguration("start_camera")
    start_base = LaunchConfiguration("start_base")
    start_lidar = LaunchConfiguration("start_lidar")
    start_arm = LaunchConfiguration("start_arm")
    start_nuc_profile = LaunchConfiguration("start_nuc_profile")
    camera_name = LaunchConfiguration("camera_name")
    camera_serial_no = LaunchConfiguration("camera_serial_no")
    base_can_port = LaunchConfiguration("base_can_port")
    piper_can_port = LaunchConfiguration("piper_can_port")
    piper_auto_enable = LaunchConfiguration("piper_auto_enable")

    return LaunchDescription(
        [
            DeclareLaunchArgument("start_camera", default_value="true"),
            DeclareLaunchArgument("start_base", default_value="true"),
            DeclareLaunchArgument("start_lidar", default_value="true"),
            DeclareLaunchArgument("start_arm", default_value="false"),
            DeclareLaunchArgument("start_nuc_profile", default_value="true"),
            DeclareLaunchArgument("camera_name", default_value="d425i"),
            DeclareLaunchArgument("camera_serial_no", default_value=""),
            DeclareLaunchArgument("base_can_port", default_value="can0"),
            DeclareLaunchArgument("piper_can_port", default_value="can1"),
            DeclareLaunchArgument("piper_auto_enable", default_value="false"),
            include_hardware("nuc_ultra_profile.launch.py", start_nuc_profile),
            include_hardware(
                "realsense_d425i.launch.py",
                start_camera,
                {"camera_name": camera_name, "serial_no": camera_serial_no},
            ),
            include_hardware(
                "scout_mini_base.launch.py",
                start_base,
                {"port_name": base_can_port},
            ),
            include_hardware("mid360.launch.py", start_lidar),
            include_hardware(
                "piper_arm.launch.py",
                start_arm,
                {"can_port": piper_can_port, "auto_enable": piper_auto_enable},
            ),
        ]
    )
