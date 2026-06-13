from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("image_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument("templates_config", default_value=""),
            DeclareLaunchArgument("match_threshold", default_value="0.72"),
            DeclareLaunchArgument("save_unknown_candidates", default_value="false"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            Node(
                package="service_robot_perception",
                executable="custom_marker_detector",
                name="custom_marker_detector",
                output="screen",
                parameters=[
                    {
                        "image_topic": LaunchConfiguration("image_topic"),
                        "templates_config": LaunchConfiguration("templates_config"),
                        "result_topic": "/perception/custom_marker/result",
                        "annotated_topic": "/perception/custom_marker/annotated",
                        "match_threshold": ParameterValue(
                            LaunchConfiguration("match_threshold"), value_type=float
                        ),
                        "save_unknown_candidates": ParameterValue(
                            LaunchConfiguration("save_unknown_candidates"), value_type=bool
                        ),
                        "use_sim_time": ParameterValue(
                            LaunchConfiguration("use_sim_time"), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
