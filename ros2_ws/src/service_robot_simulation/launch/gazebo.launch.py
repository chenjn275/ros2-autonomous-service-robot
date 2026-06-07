from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")
    gui = LaunchConfiguration("gui")
    robot_description_path = PathJoinSubstitution(
        [FindPackageShare("service_robot_description"), "urdf", "service_robot.urdf.xacro"]
    )
    world_path = PathJoinSubstitution(
        [FindPackageShare("service_robot_simulation"), "worlds", "indoor_room.world"]
    )
    robot_description = {
        "robot_description": Command(
            ["xacro ", robot_description_path, " use_gazebo:=true"]
        )
    }

    actions = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[robot_description, {"use_sim_time": use_sim_time}],
        )
    ]

    try:
        gazebo_share = get_package_share_directory("gazebo_ros")
    except PackageNotFoundError:
        actions.append(
            LogInfo(
                msg=(
                    "gazebo_ros is not installed. Install ros-humble-gazebo-ros-pkgs "
                    "or run scripts/install_deps.sh before starting simulation."
                )
            )
        )
        return actions

    actions.extend(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([gazebo_share, "launch", "gzserver.launch.py"])
                ),
                launch_arguments={
                    "world": world_path,
                    "verbose": "false",
                    "factory": "true",
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([gazebo_share, "launch", "gzclient.launch.py"])
                ),
                condition=IfCondition(gui),
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-topic", "robot_description", "-entity", "service_robot"],
                output="screen",
            ),
        ]
    )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("gui", default_value="false"),
            OpaqueFunction(function=launch_setup),
        ]
    )
