from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from launch_ros.substitutions import FindPackageShare
from nav2_common.launch import RewrittenYaml


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    bond_timeout = LaunchConfiguration("bond_timeout")
    map_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")
    log_level = LaunchConfiguration("log_level")

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key="",
            param_rewrites={
                "use_sim_time": use_sim_time,
                "yaml_filename": map_file,
            },
            convert_types=True,
        ),
        allow_substs=True,
    )

    remappings = [("/tf", "tf"), ("/tf_static", "tf_static")]
    localization_lifecycle_nodes = ["map_server", "amcl"]
    navigation_lifecycle_nodes = [
        "controller_server",
        "smoother_server",
        "planner_server",
        "behavior_server",
        "bt_navigator",
    ]

    common_node_args = {
        "output": "screen",
        "parameters": [configured_params],
        "arguments": ["--ros-args", "--log-level", log_level],
        "remappings": remappings,
    }

    return [
        LogInfo(msg="Starting minimal Nav2 stack without velocity_smoother."),
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            **common_node_args,
        ),
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            **common_node_args,
        ),
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            **common_node_args,
        ),
        Node(
            package="nav2_smoother",
            executable="smoother_server",
            name="smoother_server",
            **common_node_args,
        ),
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            **common_node_args,
        ),
        Node(
            package="nav2_behaviors",
            executable="behavior_server",
            name="behavior_server",
            **common_node_args,
        ),
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            **common_node_args,
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_localization",
            output="screen",
            arguments=["--ros-args", "--log-level", log_level],
            parameters=[
                {"use_sim_time": use_sim_time},
                {"autostart": autostart},
                {"bond_timeout": bond_timeout},
                {"node_names": localization_lifecycle_nodes},
            ],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            output="screen",
            arguments=["--ros-args", "--log-level", log_level],
            parameters=[
                {"use_sim_time": use_sim_time},
                {"autostart": autostart},
                {"bond_timeout": bond_timeout},
                {"node_names": navigation_lifecycle_nodes},
            ],
        ),
    ]


def generate_launch_description():
    default_map = PathJoinSubstitution(
        [FindPackageShare("service_robot_navigation"), "maps", "demo_map.yaml"]
    )
    default_params = PathJoinSubstitution(
        [FindPackageShare("service_robot_navigation"), "config", "nav2_params.yaml"]
    )

    return LaunchDescription(
        [
            SetEnvironmentVariable("RCUTILS_LOGGING_BUFFERED_STREAM", "1"),
            DeclareLaunchArgument("map", default_value=default_map),
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("autostart", default_value="true"),
            DeclareLaunchArgument("bond_timeout", default_value="20.0"),
            DeclareLaunchArgument("log_level", default_value="info"),
            OpaqueFunction(function=launch_setup),
        ]
    )
