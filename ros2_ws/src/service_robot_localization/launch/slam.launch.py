from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory


def launch_setup(context, *args, **kwargs):
    try:
        get_package_share_directory("slam_toolbox")
    except PackageNotFoundError:
        return [
            LogInfo(
                msg=(
                    "slam_toolbox is not installed. Install ros-humble-slam-toolbox "
                    "or run scripts/install_deps.sh before starting SLAM."
                )
            )
        ]

    return [
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[
                LaunchConfiguration("params_file"),
                {"use_sim_time": LaunchConfiguration("use_sim_time")},
            ],
        )
    ]


def generate_launch_description():
    default_params = PathJoinSubstitution(
        [
            FindPackageShare("service_robot_localization"),
            "config",
            "slam_toolbox.yaml",
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("params_file", default_value=default_params),
            OpaqueFunction(function=launch_setup),
        ]
    )
