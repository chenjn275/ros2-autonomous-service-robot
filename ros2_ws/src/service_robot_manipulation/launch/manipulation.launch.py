from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory


def launch_setup(context, *args, **kwargs):
    robot_model = LaunchConfiguration("robot_model").perform(context)
    demo_mode = LaunchConfiguration("demo_mode").perform(context)

    if demo_mode != "panda":
        return [
            LogInfo(
                msg=(
                    "service_robot manipulation config is not generated yet. Use "
                    "demo_mode:=panda to launch a headless MoveIt2 Panda move_group demo, "
                    "or create service_robot_moveit_config for the real service robot arm. "
                    f"Requested robot_model={robot_model}."
                )
            )
        ]

    try:
        get_package_share_directory("moveit_ros_move_group")
        get_package_share_directory("moveit_resources_panda_moveit_config")
        get_package_share_directory("moveit_resources_panda_description")
    except PackageNotFoundError:
        return [
            LogInfo(
                msg=(
                    "MoveIt2 Panda demo dependencies are not installed. Install "
                    "ros-humble-moveit, ros-humble-moveit-resources-panda-description, "
                    "and ros-humble-moveit-resources-panda-moveit-config."
                )
            )
        ]

    from moveit_configs_utils import MoveItConfigsBuilder

    moveit_config = (
        MoveItConfigsBuilder("moveit_resources_panda")
        .robot_description(file_path="config/panda.urdf.xacro")
        .robot_description_semantic(file_path="config/panda.srdf")
        .trajectory_execution(file_path="config/gripper_moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"])
        .to_moveit_configs()
    )

    return [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="panda_static_transform_publisher",
            output="screen",
            arguments=[
                "--x",
                "0",
                "--y",
                "0",
                "--z",
                "0",
                "--roll",
                "0",
                "--pitch",
                "0",
                "--yaw",
                "0",
                "--frame-id",
                "world",
                "--child-frame-id",
                "panda_link0",
            ],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="panda_robot_state_publisher",
            output="screen",
            parameters=[moveit_config.robot_description],
        ),
        Node(
            package="moveit_ros_move_group",
            executable="move_group",
            name="move_group",
            output="screen",
            parameters=[moveit_config.to_dict()],
            arguments=["--ros-args", "--log-level", "info"],
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_model", default_value="piper"),
            DeclareLaunchArgument("demo_mode", default_value="service_robot"),
            OpaqueFunction(function=launch_setup),
        ]
    )
