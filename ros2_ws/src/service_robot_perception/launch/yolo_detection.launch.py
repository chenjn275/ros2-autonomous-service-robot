from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("image_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument("model_path", default_value=""),
            DeclareLaunchArgument("confidence", default_value="0.25"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            Node(
                package="service_robot_perception",
                executable="yolo_detector",
                name="yolo_detector",
                output="screen",
                parameters=[
                    {
                        "image_topic": LaunchConfiguration("image_topic"),
                        "detections_topic": "/perception/yolo/detections",
                        "annotated_topic": "/perception/yolo/annotated",
                        "model_path": LaunchConfiguration("model_path"),
                        "confidence": LaunchConfiguration("confidence"),
                        "use_sim_time": ParameterValue(
                            LaunchConfiguration("use_sim_time"), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
