from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include_perception_launch(launch_file, launch_arguments=None, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("service_robot_perception"),
                    "launch",
                    launch_file,
                ]
            )
        ),
        launch_arguments=(launch_arguments or {}).items(),
        condition=condition,
    )


def generate_launch_description():
    image_topic = LaunchConfiguration("image_topic")
    yolo_model_path = LaunchConfiguration("yolo_model_path")
    yolo_confidence = LaunchConfiguration("yolo_confidence")
    marker_templates_config = LaunchConfiguration("marker_templates_config")
    marker_match_threshold = LaunchConfiguration("marker_match_threshold")
    start_yolo = LaunchConfiguration("start_yolo")
    start_markers = LaunchConfiguration("start_markers")
    use_sim_time = LaunchConfiguration("use_sim_time")

    return LaunchDescription(
        [
            DeclareLaunchArgument("image_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument(
                "yolo_model_path",
                default_value="/home/chen/model_backup/craic_items_baseline_best.pt",
            ),
            DeclareLaunchArgument("yolo_confidence", default_value="0.45"),
            DeclareLaunchArgument("marker_templates_config", default_value=""),
            DeclareLaunchArgument("marker_match_threshold", default_value="0.65"),
            DeclareLaunchArgument("start_yolo", default_value="true"),
            DeclareLaunchArgument("start_markers", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            include_perception_launch(
                "custom_marker_detection.launch.py",
                condition=IfCondition(start_markers),
                launch_arguments={
                    "image_topic": image_topic,
                    "templates_config": marker_templates_config,
                    "match_threshold": marker_match_threshold,
                    "use_sim_time": use_sim_time,
                },
            ),
            include_perception_launch(
                "yolo_detection.launch.py",
                condition=IfCondition(start_yolo),
                launch_arguments={
                    "image_topic": image_topic,
                    "model_path": yolo_model_path,
                    "confidence": yolo_confidence,
                    "use_sim_time": use_sim_time,
                },
            ),
        ]
    )
