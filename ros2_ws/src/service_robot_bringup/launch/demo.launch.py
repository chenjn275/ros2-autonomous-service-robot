from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include(package_name, launch_file, condition=None, launch_arguments=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare(package_name),
                    "launch",
                    launch_file,
                ]
            )
        ),
        condition=condition,
        launch_arguments=(launch_arguments or {}).items(),
    )


def generate_launch_description():
    gui = LaunchConfiguration("gui")
    use_sim_time = LaunchConfiguration("use_sim_time")
    start_perception = LaunchConfiguration("start_perception")
    start_tasks = LaunchConfiguration("start_tasks")
    start_system = LaunchConfiguration("start_system")
    task_start_delay_sec = LaunchConfiguration("task_start_delay_sec")

    return LaunchDescription(
        [
            DeclareLaunchArgument("gui", default_value="false"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("start_perception", default_value="true"),
            DeclareLaunchArgument("start_tasks", default_value="true"),
            DeclareLaunchArgument("start_system", default_value="true"),
            DeclareLaunchArgument("task_start_delay_sec", default_value="1.0"),
            include(
                "service_robot_simulation",
                "gazebo.launch.py",
                launch_arguments={"gui": gui},
            ),
            include(
                "service_robot_perception",
                "qr_detection.launch.py",
                condition=IfCondition(start_perception),
                launch_arguments={"use_sim_time": use_sim_time},
            ),
            include(
                "service_robot_perception",
                "yolo_detection.launch.py",
                condition=IfCondition(start_perception),
                launch_arguments={"use_sim_time": use_sim_time},
            ),
            include(
                "service_robot_system",
                "system_health.launch.py",
                condition=IfCondition(start_system),
            ),
            include(
                "service_robot_tasks",
                "task_commander.launch.py",
                condition=IfCondition(start_tasks),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                    "use_nav": "false",
                    "start_delay_sec": task_start_delay_sec,
                },
            )
        ]
    )
