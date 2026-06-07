from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    default_config = PathJoinSubstitution(
        [FindPackageShare("service_robot_tasks"), "config", "home_sorting_demo.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("mission_config", default_value=default_config),
            DeclareLaunchArgument("use_nav", default_value="false"),
            DeclareLaunchArgument("mock_nav_delay_sec", default_value="0.5"),
            DeclareLaunchArgument("default_nav_timeout_sec", default_value="20.0"),
            DeclareLaunchArgument("nav_server_wait_sec", default_value="30.0"),
            DeclareLaunchArgument("nav_goal_send_timeout_sec", default_value="30.0"),
            DeclareLaunchArgument("start_delay_sec", default_value="1.0"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            Node(
                package="service_robot_tasks",
                executable="task_commander",
                name="task_commander",
                output="screen",
                parameters=[
                    {
                        "mission_config": LaunchConfiguration("mission_config"),
                        "use_nav": ParameterValue(LaunchConfiguration("use_nav"), value_type=bool),
                        "mock_nav_delay_sec": ParameterValue(
                            LaunchConfiguration("mock_nav_delay_sec"), value_type=float
                        ),
                        "default_nav_timeout_sec": ParameterValue(
                            LaunchConfiguration("default_nav_timeout_sec"), value_type=float
                        ),
                        "nav_server_wait_sec": ParameterValue(
                            LaunchConfiguration("nav_server_wait_sec"), value_type=float
                        ),
                        "nav_goal_send_timeout_sec": ParameterValue(
                            LaunchConfiguration("nav_goal_send_timeout_sec"), value_type=float
                        ),
                        "start_delay_sec": ParameterValue(
                            LaunchConfiguration("start_delay_sec"), value_type=float
                        ),
                        "use_sim_time": ParameterValue(
                            LaunchConfiguration("use_sim_time"), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
