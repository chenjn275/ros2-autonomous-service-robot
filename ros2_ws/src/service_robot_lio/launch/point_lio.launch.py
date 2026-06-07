from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory


def launch_setup(context, *args, **kwargs):
    try:
        get_package_share_directory("point_lio")
    except PackageNotFoundError:
        return [
            LogInfo(
                msg=(
                    "point_lio package is not installed. Add the Point-LIO ROS2 package "
                    "to ros2_ws/src or install it before enabling this launch."
                )
            )
        ]

    return [
        Node(
            package="point_lio",
            executable="pointlio_mapping",
            name="point_lio",
            output="screen",
            parameters=[LaunchConfiguration("params_file")],
            remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        )
    ]


def generate_launch_description():
    default_params = PathJoinSubstitution(
        [FindPackageShare("service_robot_lio"), "config", "point_lio_service_robot.yaml"]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            OpaqueFunction(function=launch_setup),
        ]
    )
